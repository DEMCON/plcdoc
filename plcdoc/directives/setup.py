from sphinx.application import Sphinx
from sphinx.directives import SphinxDirective

from typing import List


class PlcDocDirective(SphinxDirective):
    required_arguments = 0
    optional_arguments = 1
    has_content = False

    def run(self) -> List:

        print("Arguments:", self.arguments)

        return []


def setup(app: Sphinx):
    """Initialize Sphinx extension."""

    app.add_directive("plcdocdirective", PlcDocDirective)
