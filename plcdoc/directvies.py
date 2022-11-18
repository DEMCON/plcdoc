from sphinx.directives import SphinxDirective
from docutils import nodes
from docutils.nodes import Node
from typing import List


class BaseDirective(SphinxDirective):
    """Base for each directive in the plcdoc extension."""

    required_arguments = 1
    optional_arguments = 0
    has_content = True
    final_argument_whitespace = True


class PlcDocFunctionDirective(BaseDirective):

    required_arguments = 0
    optional_arguments = 1
    has_content = False

    def run(self) -> List[Node]:
        return self.render()

    def render(self) -> List[Node]:
        node = nodes.paragraph(text="Hello world!")
        return [node]


class PlcDocFunctionBlockDirective(BaseDirective):

    def run(self) -> List[Node]:

        analyzer = self.env.app._plcdoc_analyzer

        node = nodes.paragraph(text="I am `PlcDocFunctionBlockDirective`")
        return [node]
