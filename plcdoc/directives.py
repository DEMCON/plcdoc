import re
from typing import List, Tuple
import re

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.directives import SphinxDirective, ObjectDescription
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.domains.python import _pseudo_parse_arglist, _parse_annotation


# Regex for unofficial PLC signatures
plc_sig_re = re.compile(
    r"""^ (\w+)  \s*                    # thing name
          (?: \(\s*(.*)\s*\)            # optional: arguments
          (?:\s* : \s* (.*))?           #           return annotation
          (?:\s* EXTENDS \s* (.*))?     #           extends
          )? $                          # and nothing more
    """,
    re.VERBOSE
)


class PlcObject(ObjectDescription):
    """Base class for description directives (e.g. for `function`).

    :cvar has_arguments: True if this type of description has a list of arguments
    """

    has_arguments = False

    option_spec = {"noindex": directives.flag}

    # None: determine automatically, False: do not use, str: use literal value
    object_display_type = None

    def handle_signature(
        self, sig: str, signode: addnodes.desc_signature
    ) -> Tuple[str, str]:
        """Break down Structured Text signatures.

        This often won't be enough, because IN, OUT and IN_OUT variables are not defined with the block declaration.
        Further declaration will have to rely on commands like `:var_in:`.
        Even though not valid PLC syntax, an argument list after the name is processed in Python style.
        """
        m = plc_sig_re.match(sig)
        if m is None:
            raise ValueError
        name, arglist, retann, extends = m.groups()

        signode["fullname"] = name

        sig_prefix = self.get_signature_prefix(sig)
        if sig_prefix:
            signode += addnodes.desc_annotation(str(sig_prefix), "", *sig_prefix)

        signode += addnodes.desc_name("", "", addnodes.desc_sig_name(name, name))

        if self.has_arguments:
            if not arglist:
                signode += addnodes.desc_parameterlist()
            else:
                _pseudo_parse_arglist(signode, arglist)

        if retann:
            children = _parse_annotation(retann, self.env)
            signode += addnodes.desc_returns(retann, "", *children)

        return name, ""

    def get_signature_prefix(self, sig: str) -> List[nodes.Node]:
        """Return a prefix to put before the object name in the signature."""

        if self.object_display_type is None:
            objtype = self.objtype.upper()
            objtype = objtype.replace("BLOCK", "_BLOCK")
        elif self.object_display_type:
            objtype = self.object_display_type
        else:
            return []

        return [nodes.Text(objtype), addnodes.desc_sig_space()]


class PlcCallable(PlcObject):
    """Directive to describe a callable object (function, function block)."""

    has_arguments = True

    # fmt: off
    doc_field_types = [
        TypedField(
            "var_in",
            label="VAR_IN",
            names=("var_in", "VAR_IN", "in", "IN", "param", "parameter", "arg", "argument"),
            typerolename="type",
            typenames=("paramtype", "type"),
            can_collapse=True,
        ),
        TypedField(
            "var_out",
            label="VAR_OUT",
            names=("var_out", "VAR_OUT", "out", "OUT"),
            typerolename="type",
            typenames=("paramtype", "type"),
            can_collapse=True,
        ),
        TypedField(
            "var_in_out",
            label="VAR_IN_OUT",
            names=("var_in_out", "VAR_IN_OUT", "in_out", "IN_OUT"),
            typerolename="type",
            typenames=("paramtype", "type"),
            can_collapse=True,
        ),
        Field(
            "returnvalue",
            label="Returns",
            has_arg=False,
            names=("returns", "return", "RETURNS", "RETURN"),
        ),
        Field("returntype", label="Return type", has_arg=False, names=("rtype",)),
    ]
    # fmt: on


class PlcEnumerator(PlcObject):
    """Directive for values of enums."""

    object_display_type = False


# class AutoFunctionBlockDirective(PlcObject):
#     def run(self) -> List[Node]:
#
#         analyzer = self.env.app._plcdoc_analyzer
#
#         node = nodes.paragraph(text="I am `PlcDocFunctionBlockDirective`")
#         return [node]
