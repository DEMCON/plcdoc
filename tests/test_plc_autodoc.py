"""
Test the PLC auto-doc directives.
"""

import pytest


@pytest.mark.sphinx("dummy", testroot="plc-autodoc")
def test_domain_plc_objects(app, status, warning):
    app.builder.build_all()
