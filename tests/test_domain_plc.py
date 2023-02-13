"""
Test the PLC directives directly, for manually describing objects.
"""

import pytest


@pytest.mark.sphinx("dummy", testroot="domain-plc")
def test_domain_plc_objects(app, status, warning):
    app.builder.build_all()

    objects = app.env.domains["plc"].data["objects"]

    assert objects["FB_TypedByHand"][2] == "functionblock"
    assert objects["Orientation"][2] == "enum"
