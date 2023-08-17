import os
from typing import List, Dict, Optional
from glob import glob
import logging
import xml.etree.ElementTree as ET
from textx import metamodel_from_file, TextXSyntaxError
from textx.metamodel import TextXMetaModel

PACKAGE_DIR = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


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
        self._models: Dict[str, Dict[str, "PlcDeclaration"]] = {}

        # List of relative folders with model key,name
        self._folders: Dict[str, List["PlcDeclaration"]] = {}

        self._active_file = ""  # For better logging of errors

        self._root_folder: Optional[str] = None  # For folder references

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

        # Find project root
        self._root_folder = os.path.dirname(os.path.normpath(path))

        source_files = []

        for item_group in root:
            if not item_group.tag.endswith("ItemGroup"):
                continue

            for item in item_group:
                if item.tag.endswith("Compile"):
                    source_files.append(item.attrib["Include"])

        # The paths in the PLC Project are relative to the project file itself:
        dir_path = os.path.dirname(path)
        source_files = [
            os.path.normpath(os.path.join(dir_path, item)) for item in source_files
        ]

        if os.path.sep == "/":
            # The project will likely contain Windows paths, which can cause issues on Linux
            source_files = [path.replace("\\", "/") for path in source_files]

        return self.parse_source_files(source_files)

    def parse_source_files(self, paths: List[str]) -> bool:
        """Parse a set of source files.

        `glob` is used, so wildcards are allowed.

        :param paths: Source paths to process
        """
        result = True

        for path in paths:
            source_files = glob(path)

            if not source_files:
                logging.warning(f"Could not find file(s) in: {path}")
            else:
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

        self._active_file = filepath

        if root.tag != "TcPlcObject":
            return False

        # Files really only contain a single object per file anyway
        for item in root:
            plc_item = item.tag  # I.e. "POU"

            if plc_item not in ["DUT", "POU", "Itf"]:
                continue

            # Name is repeated inside the declaration, use it from there instead
            # name = item.attrib["Name"]

            object_model = self._parse_declaration(item)
            if object_model is None:
                continue

            obj = PlcDeclaration(object_model, filepath)

            # Methods are inside their own subtree with a `Declaration` - simply append them to the
            # object
            for node in item:
                if node.tag in ["Declaration", "Implementation"]:
                    continue
                method_model = self._parse_declaration(node)
                if method_model is None:
                    continue
                method = PlcDeclaration(method_model, filepath)
                obj.add_child(method)

            self._add_model(obj)

        return True

    def _parse_declaration(self, item) -> Optional["TextXMetaClass"]:
        declaration_node = item.find("Declaration")
        if declaration_node is None:
            return None
        try:
            meta_model = self._meta_model.model_from_str(declaration_node.text)
            return meta_model
        except TextXSyntaxError as err:
            name = item.attrib.get("Name", "<Unknown>")
            logger.error(
                "Error parsing node `%s` in file `%s`\n(%s)",
                name,
                self._active_file,
                str(err),
            )

        return None

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

            # Build a lookup of the folders (but skip child items!)
            if self._root_folder and obj.file.startswith(self._root_folder):
                file_relative = obj.file[len(self._root_folder) :]  # Remove common path
                folder = os.path.dirname(file_relative).lstrip(os.sep)
                if folder not in self._folders:
                    self._folders[folder] = []
                self._folders[folder].append(obj)

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

        raise KeyError(f"Failed to find object `{name}` for the type `{objtype}`")

    def get_objects_in_folder(self, folder: str) -> List["PlcDeclaration"]:
        """Search for objects inside a folder.

        Currently no recursion is possible!

        :param folder: Folder name
        """
        if folder in self._folders:
            return self._folders[folder]

        raise KeyError(f"Found no models in the folder `{folder}`")


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

        if meta_model.functions:
            self._model = meta_model.functions[0]
            self._objtype = self._model.function_type.lower().replace("_", "")

        if meta_model.types:
            self._model = meta_model.types[0]
            type_str = type(self._model.type).__name__
            if "Enum" in type_str:
                self._objtype = "enum"
            elif "Struct" in type_str:
                self._objtype = "struct"
            elif "Union" in type_str:
                self._objtype = "union"
            else:
                raise ValueError(f"Could not categorize type `{type_str}`")

        if meta_model.properties:
            self._model = meta_model.properties[0]
            self._objtype = "property"

        if self._objtype is None:
            raise ValueError(f"Unrecognized declaration in `{meta_model}`")

        self._name = self._model.name
        self._file: Optional[str] = file
        self._children: Dict[str, "PlcDeclaration"] = {}

    def __repr__(self):
        type_ = type(self)
        return (
            f"<{type_.__module__}.{type_.__qualname__} object, name `{self.name}`, "
            f"at {hex(id(self))}>"
        )

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
        if hasattr(self._model, "comment") and self._model.comment is not None:
            # Probably a comment line
            big_block: str = self._model.comment.text
        elif hasattr(self._model, "comments") and self._model.comments:
            # Probably a comment block (amongst multiple maybe)
            block_comment = None
            for comment in reversed(self._model.comments):
                # Find last block-comment
                if type(comment).__name__ == "CommentBlock":
                    block_comment = comment
                    break

            if block_comment is None:
                return None

            big_block: str = block_comment.text
        else:
            return None

        big_block = big_block.strip()  # Get rid of whitespace

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
