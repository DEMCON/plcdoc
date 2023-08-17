from typing import List, Dict, Tuple, Any, NamedTuple, Optional
import re

from docutils.nodes import Element
from sphinx.addnodes import pending_xref
from sphinx.domains import Domain, ObjType
from sphinx.builders import Builder
from sphinx.environment import BuildEnvironment
from sphinx.util import logging
from sphinx.util.nodes import make_refnode, find_pending_xref_condition

from .directives import (
    PlcCallableDescription,
    PlcFunctionBlockDescription,
    PlcObjectDescription,
    PlcEnumeratorDescription,
    PlcMemberDescription,
    PlcFolderDescription,
)
from .roles import PlcXRefRole

logger = logging.getLogger(__name__)


class ObjectEntry(NamedTuple):
    docname: str
    node_id: str
    objtype: str


_builtin_types_re = re.compile(
    r"""
    (L?)REAL
    |BOOL
    |(U?)(S|D|L?)INT
""",
    re.VERBOSE,
)


class StructuredTextDomain(Domain):
    """Sphinx domain for the PLC language.

    This provides a namespace for the new PLC-specific directives, and a way of
    describing a new syntax.
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
        "member":           PlcMemberDescription,
        "property":         PlcObjectDescription,
        "folder":           PlcFolderDescription,
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
        location: Any = None,
    ) -> None:
        """Note an object for cross reference."""
        if name in self.objects:  # Duplicated
            other = self.objects[name]
            logger.warning(
                f"Duplicate object description of {name}, other instance in "
                f"{other.docname}, use :noindex: for one of them",
                location=location,
            )

        self.objects[name] = ObjectEntry(self.env.docname, node_id, objtype)

    def find_obj(
        self,
        env: BuildEnvironment,
        modname: Optional[str],
        classname: Optional[str],
        name: str,
        typ: Optional[str],
        searchmode: int = 0,
    ) -> List[Tuple[str, ObjectEntry]]:
        """Find an object for "name" in the database of objects.

        Returns a list of (name, object entry) tuples.

        The implementation is almost identical to :meth:`PythonDomain.find_obj`.

        If `searchmode` is equal to 1, the search is relaxed. The full path does not
        needto be specified.
        If `searchmode` is 0, only the full path is checked.
        """
        if name[-2:] == "()":
            name = name[:-2]

        if not name:
            return []

        matches: List[Tuple[str, ObjectEntry]] = []

        newname = None
        if searchmode == 1:
            if typ is None:
                objtypes = list(self.object_types)
            else:
                objtypes = self.objtypes_for_role(typ)
            if objtypes is not None:
                if modname and classname:
                    fullname = modname + "." + classname + "." + name
                    if (
                        fullname in self.objects
                        and self.objects[fullname].objtype in objtypes
                    ):
                        newname = fullname
                if not newname:
                    if (
                        modname
                        and modname + "." + name in self.objects
                        and self.objects[modname + "." + name].objtype in objtypes
                    ):
                        newname = modname + "." + name
                    elif (
                        name in self.objects and self.objects[name].objtype in objtypes
                    ):
                        newname = name
                    else:
                        # "fuzzy" searching mode
                        searchname = "." + name
                        matches = [
                            (oname, self.objects[oname])
                            for oname in self.objects
                            if oname.endswith(searchname)
                            and self.objects[oname].objtype in objtypes
                        ]
        else:
            # NOTE: searching for exact match, object type is not considered
            if name in self.objects:
                newname = name
            elif typ == "mod":
                # only exact matches allowed for modules
                return []
            elif classname and classname + "." + name in self.objects:
                newname = classname + "." + name
            elif modname and modname + "." + name in self.objects:
                newname = modname + "." + name
            elif (
                modname
                and classname
                and modname + "." + classname + "." + name in self.objects
            ):
                newname = modname + "." + classname + "." + name
        if newname is not None:
            matches.append((newname, self.objects[newname]))
        return matches

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> Optional[Element]:
        """Resolve cross-reference.

        Returns a reference node.

        The implementation is almost identical to :meth:`PythonDomain.resolve_xref`.
        """
        modname = None
        clsname = None
        searchmode = 1 if node.hasattr("refspecific") else 0
        matches = self.find_obj(env, modname, clsname, target, typ, searchmode)

        if not matches:
            return None
        elif len(matches) > 1:
            logger.warning(
                "[plcdoc] more than one target found for cross-reference %r: %s",
                target,
                ", ".join(match[0] for match in matches),
                type="ref",
                subtype="python",
                location=node,
            )

        name, obj = matches[0]

        if obj[2] == "module":
            # get additional info for modules
            # TODO: Reference to module
            return None
        else:
            return make_refnode(builder, fromdocname, obj[0], name, contnode, name)

    def resolve_any_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> List[Tuple[str, Element]]:
        """Resolve cross reference but without a known type."""
        modname = None
        clsname = None
        results: List[Tuple[str, Element]] = []

        # always search in "refspecific" mode with the :any: role
        matches = self.find_obj(env, modname, clsname, target, typ=None, searchmode=1)

        for name, obj in matches:
            if obj[2] == "module":
                pass  # TODO: Catch modules
            else:
                # determine the content of the reference by conditions
                content = find_pending_xref_condition(node, "resolved")
                if content:
                    children = content.children
                else:
                    # if not found, use contnode
                    children = [contnode]

                results.append(
                    (
                        "plc:" + self.role_for_objtype(obj[2]),
                        make_refnode(
                            builder, fromdocname, obj[0], obj[1], children, name
                        ),
                    )
                )
        return results

    def merge_domaindata(self, docnames: List[str], otherdata: Dict):
        pass
