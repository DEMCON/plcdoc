from sphinx.application import Sphinx
from .setup import plcdoc_setup


__version__ = "0.0.1"


def setup(app: Sphinx):
    """Initialize Sphinx extension."""

    plcdoc_setup(app)
