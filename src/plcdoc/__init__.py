from sphinx.application import Sphinx
from .setup import plcdoc_setup
from .__version__ import __version__


def setup(app: Sphinx):
    """Initialize Sphinx extension."""

    plcdoc_setup(app)
