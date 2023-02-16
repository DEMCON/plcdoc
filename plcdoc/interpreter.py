import os
from typing import List, Dict, Any, Optional
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

    # Some object types are documented the same
    EQUIVALENT_TYPES = {"function": ["function", "method"]}

    def __init__(self):
        self._meta_model = metamodel_from_file(
            os.path.join(PACKAGE_DIR, "st_declaration.tx")
        )

        # Library of processed models, keyed by the objtype and then by the name
        self._models: Dict[str, Dict[str, Any]] = {}

    def parse_plc_project(self, path: str) -> bool:
        """Parse a PLC project.

        The ``*.plcproj`` file is searched for references to source files.

        :returns: True if successful
        """
        tree = ET.parse(path)
        root = tree.getroot()

        # The items in the project XML are namespaced, so addressing each item by name does not work
        if not root.tag.endswith("Project"):
            return False

        source_files = []

        for item_group in root:
            if not item_group.tag.endswith("ItemGroup"):
                continue

            for item in item_group:
                if item.tag.endswith("Compile"):
                    source_files.append(item.attrib["Include"])

        # The paths in the PLC Project are relative to the project file itself:
        dir_path = os.path.dirname(path)
        source_files = [os.path.join(dir_path, item) for item in source_files]

        return self.parse_source_files(source_files)

    def parse_source_files(self, paths: List[str]) -> bool:
        """Parse a set of source files.

        `glob` is used, so wildcards are allowed.

        :param paths: Source paths to process
        """
        result = True

        for path in paths:
            source_files = glob(path)
            for source_file in source_files:
                if not self._parse_file(source_file):
                    result = False

        return result

    def _parse_file(self, filepath) -> bool:
        """Process a single PLC file.

        :return: True if a file was processed successfully
        """

        tree = ET.parse(filepath)
        root = tree.getroot()

        if root.tag != "TcPlcObject":
            return False

        # Files really only contain a single object per file anyway
        for item in root:
            # plc_item = item.tag  # I.e. "POU"

            # Name repeated inside the declaration, use it from there instead
            # name = item.attrib["Name"]

            object_model = self._parse_declaration(item)

            obj = PlcDeclaration(object_model, filepath)

            # Methods are inside their own subtree with a `Declaration` - simply append them to the object
            for node in item:
                if node.tag in ["Declaration", "Implementation"]:
                    continue
                method_model = self._parse_declaration(node)
                method = PlcDeclaration(method_model, filepath)
                obj.add_child(method)

            self._add_model(obj)

    def _parse_declaration(self, item):
        declaration_node = item.find("Declaration")
        meta_model = self._meta_model.model_from_str(declaration_node.text)
        return meta_model

    def reduce_type(self, key: str):
        """If key is one of multiple, return the main type.

        E.g. "method" will be reduced to "function".
        """
        for major_type, equivalents in self.EQUIVALENT_TYPES.items():
            if key in equivalents:
                return major_type

        return key

    def _add_model(
        self, obj: "PlcDeclaration", parent: Optional["PlcDeclaration"] = None
    ):
        """Get processed model and add it to our library.

        Also store references to the children of an object directly, so they can be
        found easily later.

        :param obj: Processed model
        :param parent: Object that this object belongs to
        """
        key = self.reduce_type(obj.objtype)

        name = (parent.name + "." if parent else "") + obj.name

        if key not in self._models:
            self._models[key] = {}

        self._models[key][name] = obj

        if not parent:
            for child in obj.children.values():
                self._add_model(child, obj)

    def get_object(self, name: str, objtype: Optional[str] = None) -> "PlcDeclaration":
        """Search for an object by name in parsed models.

        If ``objtype`` is `None`, any object is returned.

        :param name: Object name
        :param objtype: objtype of the object to look for ("function", etc.)
        :raises: KeyError if the object could not be found
        """
        if objtype:
            objtype = self.reduce_type(objtype)
            try:
                return self._models[objtype][name]
            except KeyError:
                pass

        else:
            for models_set in self._models.values():
                if name in models_set:
                    return models_set[name]

        raise KeyError(f"Failed to find model for `{name}`")


class PlcDeclaration:
    """Wrapper class for the result of the TextX parsing of a PLC source file.

    Instances of these declarations are stored in an interpreter object.

    An object also stores a list of all child objects (e.g. methods).

    The `objtype` is as they appear in :class:`StructuredTextDomain`.
    """

    def __init__(self, meta_model: TextXMetaModel, file=None):
        """

        :param meta_model: Parsing result
        :param file: Path to the file this model originates from
        """
        self._objtype = None

        if hasattr(meta_model, "function"):
            self._model = meta_model.function
            self._objtype = self._model.function_type.lower().replace("_", "")

        self._name = self._model.name
        self._file: Optional[str] = file
        self._children: Dict[str, "PlcDeclaration"] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def objtype(self) -> str:
        return self._objtype

    @property
    def file(self) -> str:
        return self._file or "<unknown>"

    @property
    def children(self) -> Dict[str, "PlcDeclaration"]:
        return self._children

    def get_comment(self) -> Optional[str]:
        """Process main block comment from model into a neat list.

        A list is created for each 'region' of comments. The first comment block above a declaration
        is the most common one.
        """
        if not hasattr(self._model, "comment") or self._model.comment is None:
            return None

        big_block: str = self._model.comment.comment.strip()  # Remove whitespace
        # Remove comment indicators (cannot get rid of them by TextX)
        if big_block.startswith("(*"):
            big_block = big_block[2:]
        if big_block.endswith("*)"):
            big_block = big_block[:-2]

        # It looks like Windows line endings are already lost by now, but make sure
        big_block = big_block.replace("\r\n", "\n")

        return big_block

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
            if skip_internal and var_kind not in [
                "var_input",
                "var_output",
                "var_input_output",
            ]:
                continue  # Skip internal variables `VAR`

            for var in var_list.variables:
                setattr(var, "kind", var_kind)
                args.append(var)

        return args

    def add_child(self, child: "PlcDeclaration"):
        self._children[child.name] = child
