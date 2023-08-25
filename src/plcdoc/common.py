import re

from docutils.nodes import Node, Text

from sphinx.environment import BuildEnvironment
from sphinx.addnodes import pending_xref

from typing import Optional, List


_builtin_types_re = re.compile(
    r"""
    (L?)REAL
    |BOOL
    |(U?)(S|D|L?)INT
""",
    re.VERBOSE,
)


def type_to_xref(
    target: str, env: Optional[BuildEnvironment] = None, suppress_prefix: bool = False
) -> pending_xref:
    """Convert a type string to a cross-reference node.

    This function is a direct mirror of :func:`python.type_to_xref`.
    """
    kwargs = {}

    contnodes = [Text(target)]

    return pending_xref(
        "",
        *contnodes,
        refdomain="plc",
        reftype=None,
        reftarget=target,
        refspecific=False,
        **kwargs,
    )


def _parse_annotation(annotation: str, env: Optional[BuildEnvironment]) -> List[Node]:
    """Parse type annotation to e.g. a cross-reference

    This function is a direct mirror of :func:`python._parse_annotation`.
    """
    if _builtin_types_re.match(annotation):
        return []  # Skip built-in types

    return [type_to_xref(annotation, env)]
