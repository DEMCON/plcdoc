from typing import List, Dict, Tuple, Any, NamedTuple

from docutils.nodes import Element
from sphinx.addnodes import pending_xref
from sphinx.roles import XRefRole
from sphinx.domains import Domain, ObjType
from sphinx.util import logging

from .directives import (
    PlcCallableDescription,
    PlcFunctionBlockDescription,
    PlcObjectDescription,
    PlcEnumeratorDescription,
)
from .roles import PlcXRefRole

logger = logging.getLogger(__name__)


class ObjectEntry(NamedTuple):
    docname: str
    node_id: str
    objtype: str


class StructuredTextDomain(Domain):
    """Sphinx domain for the PLC language.

    This provides a namespace for the new PLC-specific directives, and a way of describing
    a new syntax.
    """

    name = "plc"
    label = "PLC (Structured Text)"

    # fmt: off
    # Objects are all the things that Sphinx can document
    object_types = {
        "function":         ObjType("function",         "func"),
        "method":           ObjType("method",           "meth"),
        "functionblock":    ObjType("functionblock",    "funcblock",    "type"),
        "struct":           ObjType("struct",           "struct",       "type"),
        "enum":             ObjType("enum",             "enum",         "type"),
        "enumerator":       ObjType("enumerator",       "enumerator"),
    }

    directives = {
        "function":         PlcCallableDescription,
        "functionblock":    PlcFunctionBlockDescription,
        "method":           PlcCallableDescription,
        "enum":             PlcObjectDescription,
        "enumerator":       PlcEnumeratorDescription,
        "struct":           PlcObjectDescription,
        "property":         PlcObjectDescription,
    }

    # Roles are used to reference objects and are used like :rolename:`content`
    roles = {
        "func":         PlcXRefRole(),
        "meth":         PlcXRefRole(),
        "funcblock":    PlcXRefRole(),
        "struct":       PlcXRefRole(),
        "enum":         PlcXRefRole(),
        "enumerator":   PlcXRefRole(),
        "type":         PlcXRefRole(),
    }

    # fmt: on

    initial_data = {"objects": {}, "modules": {}}

    indices = []

    @property
    def objects(self) -> Dict[str, ObjectEntry]:
        return self.data.setdefault("objects", {})  # fullname -> ObjectEntry

    def note_object(
        self,
        name: str,
        objtype: str,
        node_id: str,
        aliased: bool = False,
        location: Any = None,
    ) -> None:
        """Note an object for cross reference."""
        if name in self.objects:  # Duplicated
            other = self.objects[name]
            logger.warning(
                f"Duplicate object description of {name}, other instance in {other.docname},"
                f"use :noindex: for one of them",
                location=location,
            )

        self.objects[name] = ObjectEntry(self.env.docname, node_id, objtype)

    def resolve_any_xref(
        self,
        env: "BuildEnvironment",
        fromdocname: str,
        builder: "Builder",
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> List[Tuple[str, Element]]:
        return []

    def merge_domaindata(self, docnames: List[str], otherdata: Dict):
        pass
