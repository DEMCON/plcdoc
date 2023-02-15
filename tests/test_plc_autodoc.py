"""
Test the PLC auto-doc directives.
"""

import pytest
from unittest.mock import Mock

from sphinx import addnodes
from sphinx.ext.autodoc.directive import DocumenterBridge, process_documenter_options
from sphinx.util.docutils import LoggingReporter


def do_autodoc(app, objtype, name, options=None):
    """Run specific autodoc function and get output.

    This does rely on `testroot` but no documentation is generated.
    """
    if options is None:
        options = {}
    app.env.temp_data.setdefault("docname", "index")  # set dummy docname
    doccls = app.registry.documenters[objtype]
    docoptions = process_documenter_options(doccls, app.config, options)
    state = Mock()
    state.document.settings.tab_width = 8
    bridge = DocumenterBridge(app.env, LoggingReporter(""), docoptions, 1, state)
    documenter = doccls(bridge, name)
    documenter.generate()

    return bridge.result


@pytest.mark.sphinx("dummy", testroot="plc-autodoc")
def test_autodoc_build(app, status, warning):
    """Test building a document with the PLC autodoc features."""
    app.builder.build_all()

    content = app.env.get_doctree("index")

    assert isinstance(content[2], addnodes.desc)
    assert content[2][0].astext() == "FUNCTION RegularFunction(input, other_arg)"
    assert (
        "Long description of the function, spanning multiple\nrows even"
        in content[2][1].astext()
    )

    assert isinstance(content[4], addnodes.desc)
    assert content[4][0].astext() == "FUNCTION PlainFunction()"

    assert isinstance(content[7], addnodes.desc)
    assert (
        content[7][0].astext()
        == "FUNCTION_BLOCK PlainFunctionBlock(someInput, someOutput)"
    )
    assert "someOutput (BOOL)" in content[7][1].astext()

    assert isinstance(content[9], addnodes.desc)
    assert (
        content[9][0].astext()
        == "FUNCTION_BLOCK FB_MyBlock(someInput, otherInput, secondClause, myOutput)"
    )
    assert "AnotherMethod" in content[9][1].astext()
    assert "MyMethod" in content[9][1].astext()


@pytest.mark.sphinx("html", testroot="plc-autodoc")
def test_autodoc_function(app, status, warning):
    """Test building a document with the PLC autodoc features."""

    actual = do_autodoc(app, "plc:function", "RegularFunction")

    assert ".. plc:function:: RegularFunction(input, other_arg)" in actual

    expected_end = [
        "   Short description of the function.",
        "",
        "   Long description of the function, spanning multiple",
        "   rows even.",
        "",
        "   :var_input LREAL input: This is an in-code description of some variable",
        "   :var_input UDINT other_arg:",
        "",
    ]

    assert expected_end == actual[-8:]
