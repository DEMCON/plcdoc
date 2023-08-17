"""
Extension for Sphinx to integrate TwinCAT PLC code.
"""

from sphinx.application import Sphinx
from .extension import plcdoc_setup


def setup(app: Sphinx):
    """Initialize Sphinx extension."""

    plcdoc_setup(app)
