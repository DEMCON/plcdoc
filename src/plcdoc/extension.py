"""Contains the technical Sphinx extension stuff."""

from typing import Dict, Optional
import logging
from sphinx.application import Sphinx
from docutils.nodes import Element
from sphinx.addnodes import pending_xref
from sphinx.environment import BuildEnvironment

from .__version__ import __version__
from .interpreter import PlcInterpreter
from .domain import StructuredTextDomain
from .auto_directives import PlcAutodocDirective
from .documenters import (
    PlcFunctionBlockDocumenter,
    PlcFunctionDocumenter,
    PlcMethodDocumenter,
    PlcPropertyDocumenter,
    PlcStructDocumenter,
    PlcStructMemberDocumenter,
    PlcFolderDocumenter,
)
from .common import _builtin_types_re

logger = logging.getLogger(__name__)


def plcdoc_setup(app: Sphinx) -> Dict:
    """Initialize the plcdoc extension.

    Real setup function is put in the module ``__init__``.
    """

    # We place a callback for Sphinx for when the builder is about ready to start to
    # index the PLC files. The moment of reading the PLC files could probably be
    # anything.

    app.setup_extension("sphinx.ext.autodoc")  # Require the autodoc extension

    app.connect("builder-inited", analyze)

    app.add_config_value("plc_sources", [], True)  # List[str]
    app.add_config_value("plc_project", None, True)  # str

    app.add_domain(StructuredTextDomain)

    app.registry.add_documenter("plc:function", PlcFunctionDocumenter)
    app.add_directive_to_domain("plc", "autofunction", PlcAutodocDirective)

    app.registry.add_documenter("plc:functionblock", PlcFunctionBlockDocumenter)
    app.add_directive_to_domain("plc", "autofunctionblock", PlcAutodocDirective)

    app.registry.add_documenter("plc:method", PlcMethodDocumenter)
    app.add_directive_to_domain("plc", "automethod", PlcAutodocDirective)

    app.registry.add_documenter("plc:property", PlcPropertyDocumenter)
    app.add_directive_to_domain("plc", "autoproperty", PlcAutodocDirective)

    app.registry.add_documenter("plc:struct", PlcStructDocumenter)
    app.registry.add_documenter("plc:member", PlcStructMemberDocumenter)
    app.add_directive_to_domain("plc", "autostruct", PlcAutodocDirective)

    app.registry.add_documenter("plc:folder", PlcFolderDocumenter)
    app.add_directive_to_domain("plc", "autofolder", PlcAutodocDirective)

    # Insert a resolver for built-in types
    app.connect("missing-reference", builtin_resolver, priority=900)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def analyze(app: Sphinx):
    """Perform the analysis of PLC source and extract docs.

    The sources to be scoured are listed in the user's ``conf.py``.

    The analysed results need to be available throughout the rest of the extension. To
    accomplish that, we just insert a new property into ``app``.
    """

    # Inserting the shared interpreter into an existing object is not the neatest, but
    # it's the best way to keep an instance linked to an `app` object. The alternative
    # would be the `app.env.temp_data` dict, which is also nasty.
    interpreter = PlcInterpreter()

    source_paths = (
        [app.config.plc_sources]
        if isinstance(app.config.plc_sources, str)
        else app.config.plc_sources
    )
    if source_paths:
        if not interpreter.parse_source_files(source_paths):
            logger.warning("Could not parse all files in `plc_sources` from conf.py")

    project_file = app.config.plc_project
    if project_file:
        if not interpreter.parse_plc_project(project_file):
            logger.warning(
                f"Could not parse all files found in project file {project_file}"
            )

    app._interpreter = interpreter


def builtin_resolver(
    app: Sphinx, env: BuildEnvironment, node: pending_xref, contnode: Element
) -> Optional[Element]:
    """Do not emit nitpicky warnings for built-in types.

    Strongly based on :func:`python.builtin_resolver`.
    """
    # This seems to be the case when using the signature notation, e.g. `func(x: LREAL)`
    if node.get("refdomain") not in ("plc"):
        return None  # We can only deal with the PLC domain
    elif node.get("reftype") in ("class", "obj") and node.get("reftarget") == "None":
        return contnode
    elif node.get("reftype") in ("class", "obj", "type"):
        reftarget = node.get("reftarget")
        if _builtin_types_re.match(reftarget):
            return contnode

    return None
