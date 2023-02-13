import os
from typing import Dict
from sphinx.application import Sphinx

from .__version__ import __version__
from .interpreter import PlcInterpreter
from .domain import StructuredTextDomain
from .auto_directives import PlcAutodocDirective
from .documenters import (
    PlcFunctionBlockDocumenter,
    PlcFunctionDocumenter,
    PlcMethodDocumenter,
)


def plcdoc_setup(app: Sphinx) -> Dict:
    """Initialize Sphinx extension."""

    # We place a callback for Sphinx for when the builder is about ready to start to index the PLC files
    # The moment of reading the PLC files could probably be anything.

    app.connect("builder-inited", analyze)

    app.add_config_value("plc_sources", [], True)  # List[str]

    app.add_domain(StructuredTextDomain)

    app.registry.add_documenter("plc:function", PlcFunctionDocumenter)
    app.add_directive_to_domain("plc", "autofunction", PlcAutodocDirective)

    app.registry.add_documenter("plc:functionblock", PlcFunctionBlockDocumenter)
    app.add_directive_to_domain("plc", "autofunctionblock", PlcAutodocDirective)

    app.registry.add_documenter("plc:method", PlcMethodDocumenter)
    app.add_directive_to_domain("plc", "automethod", PlcAutodocDirective)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def analyze(app: Sphinx):
    """Perform the analysis of PLC source and extract docs.

    The sources to be scoured are listed in the user's ``conf.py``.

    The analysed results need to be available throughout the rest of the extension. To accomplish that, we just insert
    a new property into ``app``.
    """

    source_paths = (
        [app.config.plc_sources]
        if isinstance(app.config.plc_sources, str)
        else app.config.plc_sources
    )

    abs_source_paths = [
        os.path.normpath(os.path.join(app.confdir, path)) for path in source_paths
    ]

    # Inserting the shared interpreter into an existing object is not the most neat, but it's the best way
    # to keep an instance linked to an `app` object. The alternative would be the `app.env.temp_data` dict, which is
    # also nasty.
    interpreter = PlcInterpreter(abs_source_paths, app)
    setattr(app, "_interpreter", interpreter)
