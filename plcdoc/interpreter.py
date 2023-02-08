import os
import re
from typing import List, Dict, Any, Optional
from sphinx.application import Sphinx
from glob import glob
import xml.etree.ElementTree as ET
from textx import metamodel_from_file
from textx.metamodel import TextXMetaModel

PACKAGE_DIR = os.path.dirname(__file__)


class PlcInterpreter:
    """Class to perform the PLC file parsing.

    It uses TextX with a declaration to parse the files.

    The parsed objects are stored as their raw TextX format, as meta-models
    """

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

        :return: True if a file was processed successfully
        """

        tree = ET.parse(filepath)
        root = tree.getroot()

        if root.tag != "TcPlcObject":
            return False

        for item in root:
            plc_item = item.tag
            name = item.attrib["Name"]

            declaration_node = item.find("Declaration")

            meta_model = self._meta_model.model_from_str(declaration_node.text)

            obj = PlcDeclaration(meta_model)

            self.add_model(obj)

    def add_model(self, obj: "PlcDeclaration"):
        """Get processed model and add it to our library.

        :param obj: Processed model
        """
        self._models[obj.name] = obj

    def get_object(self, name: str) -> "PlcDeclaration":
        """Search for an object by name in parsed models.

        :param name: Object name
        :raises: KeyError if the object could not be found
        """
        return self._models[name]


class PlcDeclaration:
    """Wrapper class for the result of the TextX parsing of a PLC source file.

    Instances of these declarations are stored in an interpreter object.
    """

    def __init__(self, meta_model: TextXMetaModel):
        """

        :param meta_model: Parsing result
        """
        if hasattr(meta_model, "function"):
            self._model = meta_model.function

        self._name = self._model.name
        self._comment = self._make_comment()

    @property
    def name(self) -> str:
        return self._name

    @property
    def comment(self) -> Optional[str]:
        return self._comment

    def get_args(self, skip_internal=True) -> List:
        """Return arguments.

        :param skip_internal: If true, only return in, out and inout variables
        :retval: Empty list if there are none or arguments are applicable to this type.
        """
        if not hasattr(self._model, "lists"):
            return []

        args = []

        for var_list in self._model.lists:
            var_kind = var_list.name.lower()
            if skip_internal and var_kind not in ["var_input", "var_output", "var_input_output"]:
                continue  # Skip internal variables `VAR`

            for var in var_list.variables:
                setattr(var, "kind", var_kind)
                args.append(var)

        return args

    def _make_comment(self) -> Optional[str]:
        """Process main block comment from model into a neat list.

        A list is created for each 'region' of comments. The first comment block above a declaration
        if the most common one.
        """
        if not hasattr(self._model, "comment"):
            return None

        big_block: str = self._model.comment.comment.strip()  # Remove whitespace
        # Remove comment indicators (cannot get rid of them by TextX)
        if big_block.startswith("(*"):
            big_block = big_block[2:]
        if big_block.endswith("*)"):
            big_block = big_block[:-2]

        return big_block
