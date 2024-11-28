"""
Test PLC documentation when loading in a *.plcproj file.
"""

import pytest


@pytest.mark.sphinx("dummy", testroot="plc-project")
def test_project_interpret(app, status, warning):
    """Test building a document loading a project."""

    assert hasattr(app, "_interpreter")

    interpreter = getattr(app, "_interpreter")

    expected = {
        "functionblock": ["FB_MyBlock", "FB_SecondBlock", "PlainFunctionBlock"],
        "function": ["PlainFunction", "RegularFunction"],
        "program": ["MAIN"],
        "enum": ["E_Error"],
        "struct": ["ST_MyStruct"],
    }

    for objtype, objects in expected.items():
        for obj in objects:
            try:
                declaration = interpreter.get_object(obj, objtype)
                assert declaration is not None
            except KeyError:
                pytest.fail(f"Could not find expected object {obj}")


@pytest.mark.sphinx("dummy", testroot="plc-project")
def test_project_build(app, status, warning, caplog):
    """Test building a document loading a project."""
    app.builder.build_all()
    # Project contains a function with an outright syntax error, but the project
    # completes nonetheless.
