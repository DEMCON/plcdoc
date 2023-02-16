"""
Test the PLC directives directly, for manually describing objects.
"""

import pytest


@pytest.mark.sphinx("dummy", testroot="plc-ref")
def test_plc_ref_build(app, status, warning):
    app.builder.build_all()
    return
