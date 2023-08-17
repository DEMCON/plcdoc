import os.path
from abc import ABC
from typing import Any, Tuple, List, Dict, Optional, Any
import re

from sphinx.util import logging
from sphinx.ext.autodoc import (
    Documenter as AutodocDocumenter,
    members_option,
    ObjectMember,
    ObjectMembers,
    ALL,
)
from docutils.statemachine import StringList

from .interpreter import PlcInterpreter, PlcDeclaration

logger = logging.getLogger(__name__)


# Regex for unofficial PLC signatures -- this is used for non-auto
# directives for example.
plc_signature_re = re.compile(
    r"""^ ([\w.]*\.)?                       # class name(s)
          (\w+)  \s*                        # thing name
          (?:
                (?:\(\s*(.*)\s*\))?         # optional: arguments
                (?:\s* : \s* (.*))?         #           return annotation
                (?:\s* EXTENDS \s* (.*))?   #           extends
          )? $                              # and nothing more
    """,
    re.VERBOSE,
)


class PlcDocumenter(AutodocDocumenter, ABC):
    """Derived documenter base class for the PLC domain.

    These documenters are added to the registry in the extension ``setup`` callback.

    The purpose of a documenter is to generate literal reST code, that can be rendered into the
    docs, based on source code analysis.

    :cvar objtype: The object name as used for generating a directive
                   (should be overriden by different types)
    """

    domain = "plc"

    priority = 10

    def generate(
        self,
        more_content: Optional[StringList] = None,
        real_modname: str = None,
        check_module: bool = False,
        all_members: bool = False,
    ) -> None:
        """Generate reST for the object given by ``self.name``."""
        if not self.parse_name():
            logger.warning(f"Failed to parse name `{self.name}`")
            return

        if not self.import_object():
            return

        # Make sure that the result starts with an empty line.  This is
        # necessary for some situations where another directive preprocesses
        # reST and no starting newline is present
        self.add_line("", "<plc_autodoc>")

        # Format the object's signature, if any
        sig = self.format_signature()

        # Generate the directive header and options, if applicable
        self.add_directive_header(sig)
        self.add_line("", "<plc_autodoc>")  # Blank line again

        # E.g. the module directive doesn't have content
        self.indent += self.content_indent

        # Add all content (from docstrings, attribute docs etc.)
        self.add_content(more_content)

        # Document members, if possible
        self.document_members(all_members)

    def parse_name(self) -> bool:
        """Determine the full name of the target and what modules to import.

        We are going to get info from already processed content, so we don't actually have to import
        any files (this is terminology from the original ``autodoc``).

        Sets the properties `fullname`, `modname`, `retann`, `args`
        """
        try:
            # Parse the name supplied as directive argument
            path, base, args, retann, extann = plc_signature_re.match(
                self.name
            ).groups()
        except AttributeError:
            logger.warning(f"Invalid signature for auto-{self.objtype} (f{self.name})")
            return False

        modname = None
        parents = []

        self.modname, self.objpath = self.resolve_name(modname, parents, path, base)

        self.args = args
        self.retann = retann
        self.fullname = ".".join(self.objpath)

        return True

    def resolve_name(
        self, modname: str, parents: Any, path: str, base: Any
    ) -> Tuple[Optional[str], List[str]]:
        """Using the regex result, identify this object.

        Also use the environment if necessary.
        This is similar for most objects: there can be a class-like prefix followed by the name.
        """
        if path:
            mod_cls = path.rstrip(".")
        else:
            # No full path is given, search in:
            # An autodoc directive
            mod_cls = self.env.temp_data.get("plc_autodoc:class")
            # Nested class-like directive:
            if mod_cls is None:
                # TODO: Make sure `ref_context` can actually work
                mod_cls = self.env.ref_context.get("plc:functionblock")
            # Cannot be found at all
            if mod_cls is None:
                return None, parents + [base]

        _, sep, cls = mod_cls.rpartition(".")
        parents = [cls]

        return None, parents + [base]

    def format_name(self) -> str:
        """Get name to put in generated directive.

        Overriden from `autodoc` because have no `objpath` or `modname`.
        """
        return self.name

    def format_args(self, **kwargs: Any) -> Optional[str]:
        """Format arguments for signature, based on auto-data."""

        arg_strs = [f"{var.name}" for var in self.object.get_args()]

        return "(" + ", ".join(arg_strs) + ")"

    def import_object(self, raiseerror: bool = False) -> bool:
        """Imports the object given by ``self.modname``.

        Processing of source files is already done in :func:`analyse``, we look for the result here.
        In the original Python ``autodoc`` this is where target files are loaded and read.
        """
        interpreter: PlcInterpreter = self.env.app._interpreter

        try:
            self.object: PlcDeclaration = interpreter.get_object(
                self.fullname, self.objtype
            )
        except KeyError as err:
            logger.warning(err)
            return False

        return True

    def add_content(self, more_content: Optional[StringList]) -> None:
        """Add content from docstrings, attribute documentation and user."""

        # Add docstring from meta-model
        sourcename = self.get_sourcename()
        docstrings = self.get_doc()

        # Also add VARs from meta-model
        args_block = []
        for var in self.object.get_args():
            line_param = f":{var.kind} {var.type.name} {var.name}:"
            if var.comment and var.comment.text:
                line_param += " " + var.comment.text
            args_block.append(line_param)

        if args_block:
            docstrings.append(args_block)

        if docstrings is not None:
            if not docstrings:  # Empty array
                # Append at least a dummy docstring so the events are fired
                docstrings.append([])
            for i, line in enumerate(self.process_doc(docstrings)):
                self.add_line(line, sourcename, i)

        # Add additional content (e.g. from document), if present
        if more_content:
            for line, src in zip(more_content.data, more_content.items):
                self.add_line(line, src[0], src[1])

    def get_doc(self) -> Optional[List[List[str]]]:
        """Get docstring from the meta-model."""

        # Read main docblock
        comment_str = self.object.get_comment()
        if not comment_str:
            return []

        comment_lines = [line.strip() for line in comment_str.strip().split("\n")]

        return [comment_lines]

    def document_members(self, all_members: bool = False) -> None:
        """Create automatic documentation of members of the object.

        This includes methods, properties, etc.

        ``autodoc`` will skip undocumented members by default, we will document
        everything always.
        """
        return None

    def get_member_documenter(self, child: PlcDeclaration):
        """Put together a documenter for a child.

        This method is not used out of the box - call it from :meth:`document_members`.
        """
        # Find suitable documenters for this member
        classes = [
            cls
            for documenter_name, cls in self.documenters.items()
            if documenter_name.startswith("plc:")
            and cls.can_document_member(child, child.name, True, self)
        ]
        # Prefer the documenter with the highest priority
        classes.sort(key=lambda cls: cls.priority)
        return classes[-1](self.directive, child.name, self.indent)

    def get_sourcename(self) -> str:
        """Get origin of info for tracing purposes."""
        return f"{self.object.file}:declaration of {self.fullname}"

    def get_object_children(self, want_all: bool) -> Dict[str, Any]:
        """Get list of children of self.object that overlap with the member settings."""
        selected_children = {}

        if not want_all:
            if not self.options.members:
                return selected_children

            # Specific members given
            for name in self.options.members:
                if name in self.object.children:
                    selected_children[name] = self.object.children[name]
                else:
                    logger.warning(f"Cannot find {name} inside {self.fullname}")
        else:
            selected_children = self.object.children

        return selected_children


class PlcFunctionDocumenter(PlcDocumenter):
    """Documenter for the plain Function type."""

    objtype = "function"

    @classmethod
    def can_document_member(
        cls, member: PlcDeclaration, membername: str, isattr: bool, parent: Any
    ) -> bool:
        if hasattr(member, "objtype"):
            return member.objtype in ["function", "method"]

        return False


class PlcMethodDocumenter(PlcFunctionDocumenter):
    """Documenter for the Method type.

    This works both as a stand-alone directive as part of a function block.
    """

    objtype = "method"
    priority = PlcFunctionDocumenter.priority + 1
    # Methods and Functions can be documented the same, but we should prefer a method when possible

    @classmethod
    def can_document_member(
        cls, member: PlcDeclaration, membername: str, isattr: bool, parent: Any
    ) -> bool:
        if hasattr(member, "objtype"):
            return member.objtype == cls.objtype

        return False


class PlcFunctionBlockDocumenter(PlcFunctionDocumenter):
    """Documenter for the Function Block type."""

    objtype = "functionblock"

    option_spec = {
        "members": members_option,
    }

    @classmethod
    def can_document_member(
        cls, member: PlcDeclaration, membername: str, isattr: bool, parent: Any
    ) -> bool:
        if hasattr(member, "objtype"):
            return member.objtype in ["functionblock"]

        return False

    def document_members(self, all_members: bool = False) -> None:
        """Document nested members."""
        # TODO: Add documenting for members

        # Set current namespace for finding members
        self.env.temp_data["plc_autodoc:module"] = self.modname
        if self.objpath:
            self.env.temp_data["plc_autodoc:class"] = self.objpath[0]

        want_all = (
            all_members or self.options.inherited_members or self.options.members is ALL
        )

        member_documenters = [
            (self.get_member_documenter(child), False)
            for child in self.get_object_children(want_all).values()
        ]

        # TODO: Sort members

        for documenter, isattr in member_documenters:
            documenter.generate(
                all_members=True,
                real_modname="",
                check_module=False,
            )

        # Reset context
        self.env.temp_data["plc_autodoc:module"] = None
        self.env.temp_data["plc_autodoc:class"] = None


class PlcPropertyDocumenter(PlcDocumenter):
    """Document a functionblock Property."""

    objtype = "property"

    @classmethod
    def can_document_member(
        cls, member: PlcDeclaration, membername: str, isattr: bool, parent: Any
    ) -> bool:
        if hasattr(member, "objtype"):
            return member.objtype in ["property"]

        return False


class PlcFolderDocumenter(PlcDocumenter):
    """Document a folder and its contents."""

    objtype = "folder"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return False

    def parse_name(self) -> bool:
        # Input is in ``self.name``
        self.modname = None
        self.objpath = self.name

        self.args = None
        self.retann = None
        self.fullname = self.name

        return True

    def format_signature(self, **kwargs: Any) -> str:
        return ""

    def get_sourcename(self) -> str:
        return f"{self.fullname}:folder"

    def add_content(self, more_content: Optional[StringList]) -> None:
        if more_content:
            for line, src in zip(more_content.data, more_content.items):
                self.add_line(line, src[0], src[1])

    def import_object(self, raiseerror: bool = False) -> bool:
        """Override import to process the folder name."""

        interpreter: PlcInterpreter = self.env.app._interpreter

        folder = os.path.normpath(self.fullname)
        folder.strip(os.sep)

        try:
            self._contents: List[PlcDeclaration] = interpreter.get_objects_in_folder(
                folder
            )
        except KeyError as err:
            logger.warning(err)
            return False

        return True

    def document_members(self, all_members: bool = False) -> None:
        member_documenters = [
            (self.get_member_documenter(child), False) for child in self._contents
        ]

        # TODO: Sort content

        for documenter, isattr in member_documenters:
            documenter.generate(
                all_members=True,
                real_modname="",
                check_module=False,
            )
