from sphinx.application import Sphinx
from .directives.setup import setup as directives_setup


__version__ = "0.0.1"


def setup(app: Sphinx):
    """Initialize Sphinx extension."""

    # Call module setups too
    directives_setup(app)

    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}
