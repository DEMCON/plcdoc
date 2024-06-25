"""Contains the PLC StructuredText interpreter."""

import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from glob import glob
import logging
from .parsing import parse_new, nodes as ast
import xml.etree.ElementTree as ET

from textx import metamodel_from_file, TextXSyntaxError

USE_TEXTX = False
# USE_TEXTX = True

PACKAGE_DIR = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


TextXMetaClass = Any
"""Stub for the result of a TextX interpretation.

The result are nested classes. But there is no useful inheritance to use for type
checking.
"""


class PlcInterpreter:
    """Class to perform the PLC file parsing.

    It uses TextX with a declaration to parse the files.

    The parsed objects are stored as their raw TextX format, as meta-models
    """

    # Some object types are documented the same
    EQUIVALENT_TYPES = {
        "function": ["function", "method"],
        "functionblock": ["functionblock", "interface"],
    }

    # Document types (as XML nodes) that can be processed
    XML_TYPES = ["POU", "DUT", "GVL", "Itf"]

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

        # The items in the project XML are namespaced, so addressing each item by name
        # does not work
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
            # The project will likely contain Windows paths, which can cause issues
            # on Linux
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

            if plc_item not in self.XML_TYPES:
                continue

            # Name is repeated inside the declaration, use it from there instead
            # name = item.attrib["Name"]

            obj = self._parse_declaration(item, filepath)
            if obj is None:
                continue

            # Methods are inside their own subtree with a `Declaration` - simply append
            # them to the object
            for node in item:
                if node.tag in ["Declaration", "Implementation"]:
                    continue
                method = self._parse_declaration(node, filepath)
                if method is None:
                    continue
                obj.add_child(method)

            self._add_model(obj)

        return True

    def _parse_declaration(self, item, filepath) -> Optional["TextXMetaClass"]:
        declaration_node = item.find("Declaration")
        if declaration_node is None:
            return None

        if USE_TEXTX:
            try:
                meta_model = self._meta_model.model_from_str(declaration_node.text)
                return textx_model_to_declaration(meta_model, filepath)
            except TextXSyntaxError as err:
                name = item.attrib.get("Name", "<Unknown>")
                logger.error(
                    "Error parsing node `%s` in file `%s`\n(%s)",
                    name,
                    self._active_file,
                    str(err),
                )
        else:
            node = parse_new(declaration_node.text)
            return ast_node_to_plc_declaration(node, filepath)

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


def ast_node_to_plc_declaration(node, file) -> "PlcDeclaration":
    objtype = None
    name = None
    args = []
    members = []
    comment = ""

    if isinstance(node, ast.Function):
        name = node.name
        objtype = node.kind
        comment = process_comment(node.comment)
        for vl in node.variable_lists:
            for v in vl.variables:
                arg = PlcVariableDeclaration(
                    kind=vl.kind.lower(),
                    name=v.name,
                    ty=ast.type_to_text(v.ty),
                    comment=v.comment,
                )
                args.append(arg)

    elif isinstance(node, ast.TypeDef):
        name = node.name
        comment = process_comment(node.comment)
        if isinstance(node.ty, ast.Struct):
            objtype = "struct"
            for f in node.ty.fields:
                members.append(lark_field_to_var(f))
        elif isinstance(node.ty, ast.Union):
            objtype = "union"
        elif isinstance(node.ty, ast.Enum):
            objtype = "enum"
        else:
            raise ValueError(f"typedef not supported for type: {node.ty}")
    elif isinstance(node, ast.Property):
        comment = process_comment(node.comment)
        objtype = "property"
        name = node.name
    elif isinstance(node, ast.VariableList):
        if file is None:
            raise ValueError("Cannot parse GVL without file as no naming is present")
        name = os.path.splitext(os.path.basename(file))[0]
        objtype = "variable_list"
    else:
        raise ValueError(f"Unrecognized declaration in `{node}`")

    assert name is not None

    return PlcDeclaration(
        objtype, name=name, comment=comment, args=args, members=members, file=file
    )


def lark_field_to_var(field: ast.StructField) -> "PlcVariableDeclaration":
    comment = field.comment
    ty = ast.type_to_text(field.ty)
    return PlcVariableDeclaration(
        kind="member", name=field.name, ty=ty, comment=comment
    )


def textx_model_to_declaration(
    meta_model: TextXMetaClass, file=None
) -> "PlcDeclaration":
    objtype = None
    name = None
    members = []

    if meta_model.functions:
        model = meta_model.functions[0]
        objtype = model.function_type.lower().replace("_", "")

    if meta_model.types:
        model = meta_model.types[0]
        type_str = type(model.type).__name__
        if "Enum" in type_str:
            objtype = "enum"
        elif "Struct" in type_str:
            objtype = "struct"
            if model.type:
                print(model.type.members)
                # aarg
                members = [member_to_plc_declaration(m) for m in model.type.members]
        elif "Union" in type_str:
            objtype = "union"
            if model.type:
                members = [member_to_plc_declaration(m) for m in model.type.members]
        else:
            raise ValueError(f"Could not categorize type `{type_str}`")

    if meta_model.properties:
        model = meta_model.properties[0]
        objtype = "property"

    if meta_model.variable_lists:
        if file is None:
            raise ValueError("Cannot parse GVL without file as no naming is present")
        name = os.path.splitext(os.path.basename(file))[0]
        #     # GVL are annoying because no naming is present in source - we need to
        #     # extract it from the file name

        model = meta_model.variable_lists[0]
        objtype = "variable_list"

    if objtype is None:
        raise ValueError(f"Unrecognized declaration in `{meta_model}`")

    if name is None:
        name = model.name
    comment = get_comment(model)
    args = get_args(model)

    return PlcDeclaration(
        objtype, name, comment=comment, args=args, members=members, file=file
    )


def member_to_plc_declaration(member) -> "PlcVariableDeclaration":
    # print()
    name = member.name
    comment = member.comment.text if member.comment else ""
    ty = member.type.name
    return PlcVariableDeclaration(
        kind="member",
        name=name,
        ty=ty,
        comment=comment,
    )


def get_comment(_model) -> Optional[str]:
    """Process main block comment from model into a neat list.

    A list is created for each 'region' of comments. The first comment block above
    a declaration is the most common one.
    """
    if hasattr(_model, "comment") and _model.comment is not None:
        # Probably a comment line
        big_block: str = _model.comment.text
    elif hasattr(_model, "comments") and _model.comments:
        # Probably a comment block (amongst multiple maybe)
        block_comment = None
        for comment in reversed(_model.comments):
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
    return process_comment(big_block)


def process_comment(big_block):
    # Remove comment indicators (cannot get rid of them by TextX)
    if big_block.startswith("(*"):
        big_block = big_block[2:]
    if big_block.endswith("*)"):
        big_block = big_block[:-2]

    # It looks like Windows line endings are already lost by now, but make sure
    big_block = big_block.replace("\r\n", "\n")

    return big_block


def get_args(model) -> List:
    """Return arguments.

    :param skip_internal: If true, only return in, out and inout variables
    :retval: Empty list if there are none or arguments are applicable to this type.
    """
    skip_internal = True
    if not hasattr(model, "lists"):
        return []

    args = []

    for var_list in model.lists:
        var_kind = var_list.name.lower()
        if skip_internal and var_kind not in [
            "var_input",
            "var_output",
            "var_input_output",
        ]:
            continue  # Skip internal variables `VAR`

        for var in var_list.variables:
            print(var, type(var))
            args.append(textx_to_var(var_kind, var))

    return args


def textx_to_var(var_kind, var):
    name = var.name
    ty = var.type.name
    comment = var.comment.text if var.comment else ""
    return PlcVariableDeclaration(kind=var_kind, name=name, ty=ty, comment=comment)


class PlcDeclaration:
    """Wrapper class for the result of the TextX parsing of a PLC source file.

    Instances of these declarations are stored in an interpreter object.

    An object also stores a list of all child objects (e.g. methods).

    The `objtype` is as they appear in :class:`StructuredTextDomain`.
    """

    def __init__(
        self, objtype: str, name: str, comment=None, args=(), members=(), file=None
    ):
        """

        :param meta_model: Parsing result
        :param file: Path to the file this model originates from
        """
        self._objtype = objtype
        self._name = name
        self._comment = comment
        self._args = args
        self._members = members
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

    @property
    def members(self) -> List[TextXMetaClass]:
        return self._members

    @property
    def comment(self) -> Optional[str]:
        return self._comment

    @property
    def args(self) -> List:
        return self._args

    def add_child(self, child: "PlcDeclaration"):
        self._children[child.name] = child


@dataclass
class PlcVariableDeclaration:
    kind: str
    name: str
    ty: str
    comment: str
