from typing import Any, Tuple, List, Optional
import re

from sphinx.ext.autodoc import Documenter as PyDocumenter
from docutils.statemachine import StringList

from .interpreter import PlcInterpreter, PlcDeclaration


# Regex for unofficial PLC signatures -- this is used for non-auto
# directives for example.
plc_signature_re = re.compile(
    r"""^ (\w+)  \s*                    # thing name
          (?: \(\s*(.*)\s*\)            # optional: arguments
          (?:\s* : \s* (.*))?           #           return annotation
          (?:\s* EXTENDS \s* (.*))?     #           extends
          )? $                          # and nothing more
    """,
    re.VERBOSE,
)


class PlcDocumenter(PyDocumenter):
    """Derived documenter base class for the PLC domain.

    These documenters are added to the registry in the extension ``setup`` callback.

    The purpose of a documenter is to generate literal reST code, that can be rendered into the docs, based
    on source code analysis.

    :cvar objtype: The object name as used for generating a directive (should be overriden by different types)
    """

    def generate(
        self,
        more_content: Optional[StringList] = None,
        real_modname: str = None,
        check_module: bool = False,
        all_members: bool = False,
    ) -> None:
        """Generate reST for the object given by ``self.name``."""
        if not self.parse_name():
            self.directive.warn(f"Failed to parse name `{self.name}`")
            return

        if not self.import_object():
            return

        # Make sure that the result starts with an empty line.  This is
        # necessary for some situations where another directive preprocesses
        # reST and no starting newline is present
        self.add_line("", "<autodoc>")

        # Format the object's signature, if any
        sig = self.format_signature()
        # TODO: signature now always seems empty, should add something

        # Generate the directive header and options, if applicable
        self.add_directive_header(sig)
        self.add_line("", "<autodoc>")

        # E.g. the module directive doesn't have content
        self.indent += self.content_indent

        # Add all content (from docstrings, attribute docs etc.)
        self.add_content(more_content)

        # Document members, if possible
        # self.document_members(all_members)

    def parse_name(self) -> bool:
        """Determine the full name of the target and what modules to import.

        We are going to get info from already processed content, so we don't actually have to import
        any files (this is terminology from the original ``autodoc``).
        """
        try:
            # Parse the name supplied as directive argument
            name, args, retann, extann = plc_signature_re.match(self.name).groups()
        except AttributeError:
            self.directive.warn(
                f"Invalid signature for auto-{self.objtype} (f{self.name})"
            )
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

        self.object: PlcDeclaration = interpreter.get_object(self.name)

        return True

    def add_content(self, more_content: Optional[StringList]) -> None:
        """Add content from docstrings, attribute documentation and user."""

        sourcename = self.name

        # TODO: Test FunctionDocumenter and add content from code source

        # TODO: Added docs from Sphinx-style doc-block

        # docstrings = self.get_doc()
        # if not docstrings:
        #     # Append at least a dummy docstring
        #     docstrings.append([])

        # self.add_line("Lorem Ipsum", sourcename, 0)
        # self.add_line("Lorem Ipsum", sourcename, 1)

        sourcename = f"declaration of {self.name}"

        for i, line in enumerate(self.get_docstring_from_model()):
            self.add_line(line, sourcename, i)

        return

    def get_docstring_from_model(self) -> List:
        """Create Sphinx docstring based on analyzed meta-model."""

        docstrings = []

        for var in self.object.get_args():
            line_param = f":{var.kind} {var.type} {var.name}:"
            if var.comment and var.comment.comment:
                line_param += " " + var.comment.comment
            docstrings.append(line_param)

        return docstrings

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return False

    def resolve_name(
        self, modname: str, parents: Any, path: str, base: Any
    ) -> Tuple[str, List[str]]:
        return "", [""]

    domain = "plc"


class PlcFunctionBlockDocumenter(PlcDocumenter):
    """Documenter for the Function Block type."""

    objtype = "functionblock"


class PlcFunctionDocumenter(PlcDocumenter):
    """Documenter for the plain Function type."""

    objtype = "function"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return isinstance(member, PlcFunctionDocumenter)
