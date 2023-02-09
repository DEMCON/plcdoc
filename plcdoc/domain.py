from typing import List, Dict, Tuple
import re

from docutils.nodes import Element
from sphinx.addnodes import pending_xref
from sphinx.roles import XRefRole
from sphinx.domains import Domain, ObjType

from .directives import (
    PlcCallableDescription,
    PlcObjectDescription,
    PlcEnumeratorDescription,
)


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
        "functionblock":    PlcCallableDescription,
        "method":           PlcCallableDescription,
        "enum":             PlcObjectDescription,
        "enumerator":       PlcEnumeratorDescription,
        "struct":           PlcObjectDescription,
        "property":         PlcObjectDescription,
    }

    # Roles are used to reference objects and are used like :rolename:`content`
    roles = {
        "func":         XRefRole(),
        "meth":         XRefRole(),
        "funcblock":    XRefRole(),
        "struct":       XRefRole(),
        "enum":         XRefRole(),
        "enumerator":   XRefRole(),
        "type":         XRefRole(),
    }

    # fmt: on

    initial_data = {"objects": {}, "modules": {}}

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
