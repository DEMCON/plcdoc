"""
Test the PLC directives directly, for manually describing objects.
"""

import pytest


@pytest.mark.sphinx("dummy", testroot="domain-plc")
def test_domain_plc_objects(app, status, warning):
    app.builder.build_all()

    objects = app.env.domains["plc"].data["objects"]

    assert objects["BoringFunction"][2] == "function"
    assert objects["FB_TypedByHand"][2] == "functionblock"
    assert objects["FunctionBlockWithMethod"][2] == "functionblock"
    assert objects["E_Options"][2] == "enum"
    assert objects["Orientation"][2] == "enum"
    assert objects["ST_MyStruct"][2] == "struct"
    assert objects["ST_MyStruct2"][2] == "struct"
