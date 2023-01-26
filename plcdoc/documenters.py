from typing import Any, Tuple, List
import re

from sphinx.ext.autodoc import Documenter as PyDocumenter

from .analyzer import PlcAnalyzer


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
    """

    def parse_name(self) -> bool:
        """Determine the full name of the target and what modules to import.

        We are going to get info from already processed content, so we don't actually have to import
        any files (this is terminology from the original ``autodoc``).
        """
        try:
            # Parse the name supplied as directive argument
            name, args, retann, extann = plc_signature_re.match(self.name).groups()
        except AttributeError:
            self.directive.warn(f"Invalid signature for auto-{self.objtype} (f{self.name})")
            return False

        self.modname = None  # Modules and paths don't really exist or matter
        self.objpath = None

        self.args = args
        self.retann = retann
        self.fullname = name

        return True

    def import_object(self, raiseerror: bool = False) -> bool:
        """Imports the object given by ``self.modname``.

        Processing of source files is already done in ``analyse``, we look for the result here.
        In the original Python ``autodoc`` this is where target files are loaded and read.
        """
        analyzer: PlcAnalyzer = self.env.app._plcdoc_analyzer

        # TODO: Extract relevant object

        return True

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
    pass
