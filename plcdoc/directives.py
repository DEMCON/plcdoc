"""
This file contains the static directives for the PLC domain.
They are added into ``StructuredText``, they are not registered manually inside the Sphinx ``setup`` callback.
"""

from typing import List, Tuple

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.directives import SphinxDirective, ObjectDescription
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.domains.python import _pseudo_parse_arglist, _parse_annotation

from .documenters import plc_signature_re


class PlcObjectDescription(ObjectDescription):
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
        m = plc_signature_re.match(sig)
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


class PlcCallableDescription(PlcObjectDescription):
    """Directive to describe a callable object (function, function block)."""

    has_arguments = True

    # fmt: off
    doc_field_types = [
        TypedField(
            "var_in",
            label="VAR_IN",
            names=("var_in", "VAR_IN", "var_input", "VAR_INPUT", "in", "IN", "param", "parameter", "arg", "argument"),
            typerolename="type",
            typenames=("paramtype", "type"),
            can_collapse=False,
        ),
        TypedField(
            "var_out",
            label="VAR_OUT",
            names=("var_out", "VAR_OUT", "var_output", "VAR_OUTPUT", "out", "OUT"),
            typerolename="type",
            typenames=("paramtype", "type"),
            can_collapse=False,
        ),
        TypedField(
            "var_in_out",
            label="VAR_IN_OUT",
            names=("var_in_out", "VAR_IN_OUT", "var_input_output", "VAR_INPUT_OUTPUT", "in_out", "IN_OUT"),
            typerolename="type",
            typenames=("paramtype", "type"),
            can_collapse=False,
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


class PlcEnumeratorDescription(PlcObjectDescription):
    """Directive for values of enums."""

    object_display_type = False


# class AutoFunctionBlockDirective(PlcObject):
#     def run(self) -> List[Node]:
#
#         analyzer = self.env.app._plcdoc_analyzer
#
#         node = nodes.paragraph(text="I am `PlcDocFunctionBlockDirective`")
#         return [node]


class PlcDirective(SphinxDirective):

    required_arguments = 1
