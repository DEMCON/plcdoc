"""
Test the PLC directives directly, for manually describing objects.
"""

import pytest


@pytest.mark.sphinx("dummy", testroot="plc-ref")
def test_plc_ref_build(app, status, warning):
    app.builder.build_all()

    warning_str = warning.getvalue()

    assert "IDontExist" in warning_str
    assert "MyFunction" not in warning_str

    assert "DoesNotExistEither" in warning_str
    assert "MyBlock" not in warning_str

    assert "BlockReturn" not in warning_str
    assert "BlockArg" not in warning_str
