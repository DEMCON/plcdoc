"""
Test the PLC auto-doc directives.

The structure of these tests is largely copied from the tests of sphinx.ext.autodoc.
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

    actual = do_autodoc(app, "plc:function", "AutoFunction")

    assert ".. plc:function:: AutoFunction(input, other_arg, above)" in actual

    expected_end = [
        "   Short description of the function.",
        "",
        "   Long description of the function, spanning multiple",
        "   rows even.",
        "",
        "   :var_input LREAL input: This is an in-code description of some variable",
        "   :var_input UDINT other_arg:",
        '   :var_input BOOL above: This is a comment above "above"',
        "",
    ]

    assert list(actual)[-9:] == expected_end


@pytest.mark.sphinx("html", testroot="plc-autodoc")
def test_autodoc_functionblock(app, status, warning):
    """Test building a document with the PLC autodoc features."""

    options = {"members": None}
    actual = do_autodoc(app, "plc:functionblock", "AutoFunctionBlock", options)

    assert (
        ".. plc:functionblock:: AutoFunctionBlock(someInput, someOutput)" == actual[1]
    )
    assert "   .. plc:method:: AutoMethod(methodInput)" == actual[10]
    assert "   .. plc:property:: AutoProperty" == actual[18]

    assert [
        "   Some short description.",
        "",
        "   :var_input BOOL someInput: Important description",
        "   :var_output BOOL someOutput:",
        "",
    ] == actual[4:9]

    assert [
        "      Method description!",
        "",
        "      :var_input UDINT methodInput:",
        "",
    ] == actual[13:17]

    assert [
        "      Reference to a variable that might be read-only.",
        "",
    ] == actual[21:]


@pytest.mark.sphinx("html", testroot="plc-autodoc")
def test_autodoc_struct(app, status, warning):
    """Test building a document with the PLC autodoc features."""

    actual = do_autodoc(app, "plc:struct", "AutoStruct")

    assert ".. plc:struct:: AutoStruct" == actual[1]
    assert "   .. plc:member:: someDouble : LREAL" == actual[7]
    assert "   .. plc:member:: someBoolean : BOOL" == actual[13]

    assert [
        "   A definition of a struct.",
        "",
    ] == actual[4:6]

    assert [
        "      Use to store a number",
        "",
    ] == actual[10:12]

    assert [
        "      Use as a flag",
        "",
    ] == actual[16:]


@pytest.mark.sphinx("html", testroot="plc-autodoc")
def test_autodoc_gvl(app, status, warning):
    """Test building a document with the PLC autodoc features."""

    actual = do_autodoc(app, "plc:gvl", "AutoGVL")

    assert ".. plc:gvl:: AutoGVL" == actual[1]
    assert "   :var BOOL flag: Flag for the system" == actual[4]
    assert "   :var ULINT counter:" == actual[5]
    assert "   :var LREAL cycleTime: Time between PLC cycles" == actual[6]
