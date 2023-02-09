from abc import ABC
from typing import Any, Tuple, List, Optional
import re

from sphinx.util import logging
from sphinx.ext.autodoc import Documenter as PyDocumenter
from docutils.statemachine import StringList

from .interpreter import PlcInterpreter, PlcDeclaration

logger = logging.getLogger(__name__)


# Regex for unofficial PLC signatures -- this is used for non-auto
# directives for example.
plc_signature_re = re.compile(
    r"""^ ([\w.]*\.)?                   # class name(s)
          (\w+)  \s*                    # thing name
          (?: \(\s*(.*)\s*\)            # optional: arguments
          (?:\s* : \s* (.*))?           #           return annotation
          (?:\s* EXTENDS \s* (.*))?     #           extends
          )? $                          # and nothing more
    """,
    re.VERBOSE,
)


class PlcDocumenter(PyDocumenter, ABC):
    """Derived documenter base class for the PLC domain.

    These documenters are added to the registry in the extension ``setup`` callback.

    The purpose of a documenter is to generate literal reST code, that can be rendered into the docs, based
    on source code analysis.

    :cvar objtype: The object name as used for generating a directive (should be overriden by different types)
    """

    domain = "plc"

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
        """
        try:
            # Parse the name supplied as directive argument
            prefix, name, args, retann, extann = plc_signature_re.match(self.name).groups()
        except AttributeError:
            logger.warning(f"Invalid signature for auto-{self.objtype} (f{self.name})")
            return False

        self.modname = None  # Modules and paths don't really exist or matter
        self.objpath = []

        self.args = args
        self.retann = retann
        self.fullname = name

        return True

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
            self.object: PlcDeclaration = interpreter.get_object(self.name, self.objtype)
        except KeyError:
            logger.warning(f"Failed to find object `{self.name}` for the type `{self.objtype}`")
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
            line_param = f":{var.kind} {var.type} {var.name}:"
            if var.comment and var.comment.comment:
                line_param += " " + var.comment.comment
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

        comment_lines = [
            line.strip() for line in comment_str.strip().split("\n")
        ]

        return [comment_lines]

    def document_members(self, all_members: bool = False) -> None:
        """Created automatic documentation of members of the object.

        This includes methods, properties, etc.

        ``autodoc`` will skip undocumented members by default, we will document
        everything always.
        """
        return None

    def get_sourcename(self) -> str:
        """Get origin of info for tracing purposes."""
        return f"{self.object.file}:declaration of {self.fullname}"

    def resolve_name(
        self, modname: str, parents: Any, path: str, base: Any
    ) -> Tuple[str, List[str]]:
        return "", [""]


class PlcFunctionDocumenter(PlcDocumenter):
    """Documenter for the plain Function type."""

    objtype = "function"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return isinstance(member, PlcFunctionDocumenter)

    def document_members(self, all_members: bool = False) -> None:
        """Cannot document members."""
        pass


class PlcFunctionBlockDocumenter(PlcFunctionDocumenter):
    """Documenter for the Function Block type."""

    objtype = "functionblock"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return False

    def document_members(self, all_members: bool = False) -> None:
        """Cannot document members."""
        # TODO: Add documenting for members
        pass
