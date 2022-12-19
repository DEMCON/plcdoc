from typing import List

from docutils.parsers.rst import Directive
from docutils.nodes import Node

from .analyzer import PlcAnalyzer


class PlcRenderer:

    def __init__(self, directive: Directive):

        self._directive = directive
        self._name = self._directive.arguments[0]
        self._app = directive.env.app
        self._analyzer: PlcAnalyzer = self._app._plcdoc_analyzer

    def get_object(self):
        """Get parsed PLC object needed by this renderer."""
        obj = self._analyzer.get_object(self._name)
        return obj

    def rst_nodes(self) -> List[Node]:

        obj = self.get_object()

        return []


class AutoFunctionBlockRenderer(PlcRenderer):
    pass
