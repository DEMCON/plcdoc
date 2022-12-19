import os
from typing import List, Dict, Any
from sphinx.application import Sphinx
from glob import glob
import xml.etree.ElementTree as ET
from textx import metamodel_from_file

PACKAGE_DIR = os.path.dirname(__file__)


class PlcAnalyzer:
    """Class to perform the PLC file parsing."""

    def __init__(self, paths: List[str], app: Sphinx):
        """

        :param paths: Source paths to process
        :param app: Reference to Sphinx app instance
        """

        self._meta_model = metamodel_from_file(
            os.path.join(PACKAGE_DIR, "st_declaration.tx")
        )

        self._models: Dict[str, Any] = {}  # Library of processed models

        for path in paths:
            source_files = glob(path)
            for source_file in source_files:
                self.parse_file(source_file)

    def parse_file(self, filepath) -> bool:
        """Process a single PLC file.

        :return: True of a file was processed successfully
        """

        tree = ET.parse(filepath)
        root = tree.getroot()

        if root.tag != "TcPlcObject":
            return False

        for item in root:
            plc_item = item.tag
            name = item.attrib["Name"]

            declaration_node = item.find("Declaration")

            model = self._meta_model.model_from_str(declaration_node.text)

            self.add_model(model)

    def add_model(self, model):
        """Get processed model and add it to our library.

        :param model: Processed model
        """
        if hasattr(model, "function"):
            self._models[model.function.name] = model.function

    def get_object(self, name: str):
        """Search for an object by name in parsed models.

        :param name: Object name
        """
        return self._models[name]
