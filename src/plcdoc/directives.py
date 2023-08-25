"""Contains the static directives for the PLC domain.

They are added into :class:`~plcdoc.StructuredTextDomain`, they are not registered
manually inside the Sphinx :func:`~plcdoc.setup` callback.
"""

from typing import List, Tuple, TYPE_CHECKING

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import Field, TypedField
from sphinx.util.nodes import make_id
from sphinx.domains.python import _pseudo_parse_arglist

from .documenters import plc_signature_re
from .common import _parse_annotation

if TYPE_CHECKING:
    from .domain import StructuredTextDomain


class PlcObjectDescription(ObjectDescription):
    """Base class for description directives (e.g. for `function`).

    :cvar has_arguments: ``True`` if this type of description has a list of arguments
    :cvar object_display_type: ``True``: determine automatically, ``False``: do not use,
                               ``str``: use literal value
    """

    has_arguments = False

    option_spec = {
        "noindex": directives.flag,
        "noindexentry": directives.flag,
        "module": directives.unchanged,
    }

    object_display_type = True

    allow_nesting = False

    def handle_signature(
        self, sig: str, signode: addnodes.desc_signature
    ) -> Tuple[str, str]:
        """Break down Structured Text signatures.

        This often won't be enough, because IN, OUT and IN_OUT variables are not defined
        with the block declaration.
        Further declaration will have to rely on commands like `:var_in:`.
        Even though not valid PLC syntax, an argument list after the name is processed
        in Python style.

        If inside a class (i.e. function block), the current class is handled like:
        * It is stripped from the displayed name if present
        * It is added to the full name if not present

        Like ``autodoc`` a nesting stack is tracked to know if we're currently inside a
        class.
        """
        m = plc_signature_re.match(sig)
        if m is None:
            raise ValueError
        prefix, name, arglist, retann, extends = m.groups()

        # Check what class we are currently nested in
        classname = self.env.ref_context.get("plc:functionblock")
        if classname:
            if prefix and (prefix == classname or prefix.startswith(classname + ".")):
                # Classname was also typed in (ignore the dot at the end)
                fullname = prefix + name  # E.g. "MyClass.some_method"
                prefix = ""  # Remove classname from prefix, don't need it twice
            elif prefix:
                # A prefix was given but it's different from the nesting hierarchy
                fullname = classname + "." + prefix + name
            else:
                # No prefix given, rely on detected classname
                fullname = classname + "." + name
        else:
            if prefix:
                classname = prefix.rstrip(".")
                fullname = prefix + name
            else:
                classname = ""
                fullname = name

        signode["class"] = classname
        signode["fullname"] = fullname

        sig_prefix = self.get_signature_prefix(sig)
        if sig_prefix:
            signode += addnodes.desc_annotation(str(sig_prefix), "", *sig_prefix)

        if prefix:
            signode += addnodes.desc_addname(prefix, prefix)

        signode += addnodes.desc_name("", "", addnodes.desc_sig_name(name, name))

        if self.has_arguments:
            # TODO: Add type link from annotation (like return type)
            if not arglist:
                signode += addnodes.desc_parameterlist()
            else:
                _pseudo_parse_arglist(signode, arglist)

        if retann:
            children = _parse_annotation(retann, self.env)
            signode += addnodes.desc_returns(
                retann, "" if children else retann, *children
            )

        return fullname, prefix

    def get_signature_prefix(self, sig: str) -> List[nodes.Node]:
        """Return a prefix to put before the object name in the signature.

        E.g. "FUNCTION_BLOCK" or "METHOD".
        """
        if self.object_display_type is True:
            objtype = self.objtype.upper()
            objtype = objtype.replace("BLOCK", "_BLOCK")
        elif self.object_display_type is not False:
            objtype = self.object_display_type
        else:
            return []

        return [nodes.Text(objtype), addnodes.desc_sig_space()]

    def add_target_and_index(
        self, name: Tuple[str, str], sig: str, signode: addnodes.desc_signature
    ) -> None:
        """Add cross-reference IDs and entries to self.indexnode, if applicable."""
        fullname = name[0]
        node_id = make_id(self.env, self.state.document, "", fullname)
        signode["ids"].append(node_id)
        self.state.document.note_explicit_target(signode)

        domain: "StructuredTextDomain" = self.env.get_domain("plc")
        domain.note_object(fullname, self.objtype, node_id, location=signode)

    def before_content(self) -> None:
        """Called before parsing content.

        For nested objects (like methods inside a function block), this method will
        build up a stack of the nesting hierarchy.
        """
        prefix = None
        if self.names:
            # fullname and name_prefix come from the `handle_signature` method.
            # fullname represents the full object name that is constructed using
            # object nesting and explicit prefixes. `name_prefix` is the
            # explicit prefix given in a signature
            (fullname, name_prefix) = self.names[-1]
            if self.allow_nesting:
                prefix = fullname
            elif name_prefix:
                prefix = name_prefix.strip(".")
        if prefix:
            self.env.ref_context["plc:functionblock"] = prefix
            if self.allow_nesting:
                classes = self.env.ref_context.setdefault("plc:functionblocks", [])
                classes.append(prefix)

    def after_content(self) -> None:
        """Called after creating the content through nested parsing.

        Used to handle de-nesting the hierarchy.
        """
        classes = self.env.ref_context.setdefault("plc:functionblocks", [])
        if self.allow_nesting:
            try:
                classes.pop()
            except IndexError:
                pass

        self.env.ref_context["plc:functionblock"] = (
            classes[-1] if len(classes) > 0 else None
        )


class PlcCallableDescription(PlcObjectDescription):
    """Directive to describe a callable object (function, function block)."""

    has_arguments = True

    # fmt: off
    doc_field_types = [
        TypedField(
            "var_in",
            label="VAR_IN",
            names=("var_in", "VAR_IN", "var_input", "VAR_INPUT", "in", "IN", "param",
                   "parameter", "arg", "argument"),
            typerolename="type",
            typenames=("paramtype", "type", "var_in_type", "type_in"),
            can_collapse=False,
        ),
        TypedField(
            "var_out",
            label="VAR_OUT",
            names=("var_out", "VAR_OUT", "var_output", "VAR_OUTPUT", "out", "OUT"),
            typerolename="type",
            typenames=("var_out_type", "type_out"),  # Just "type" cannot be re-used!
            can_collapse=False,
        ),
        TypedField(
            "var_in_out",
            label="VAR_IN_OUT",
            names=("var_in_out", "VAR_IN_OUT", "var_input_output", "VAR_INPUT_OUTPUT",
                   "in_out", "IN_OUT"),
            typerolename="type",
            typenames=("var_in_out_type", "type_in_out"),
            can_collapse=False,
        ),
        Field(
            "returnvalue",
            label="Returns",
            has_arg=False,
            names=("returnvalue", "returns", "return", "RETURNS", "RETURN"),
        ),
        Field(
            "returntype",
            label="Return type",
            has_arg=False,
            names=("returntype", "rtype",), bodyrolename="type"),
    ]
    # fmt: on


class PlcFunctionBlockDescription(PlcCallableDescription):
    """Directive specifically for function blocks."""

    allow_nesting = True


class PlcEnumeratorDescription(PlcObjectDescription):
    """Directive for values of enums."""

    object_display_type = False

    def add_target_and_index(
        self, name: Tuple[str, str], sig: str, signode: addnodes.desc_signature
    ) -> None:
        # Do not index
        # TODO: Fix indexing for enums
        return


class PlcMemberDescription(PlcObjectDescription):
    """Directive specifically for (struct) members."""

    object_display_type = False


class PlcFolderDescription(PlcObjectDescription):
    """Directive specifically for a folder and contents."""

    allow_nesting = True

    def handle_signature(
        self, sig: str, signode: addnodes.desc_signature
    ) -> Tuple[str, str]:
        # Folder name does not require any parsing
        signode["fullname"] = sig

        sig_prefix = self.get_signature_prefix("folder")
        signode += addnodes.desc_annotation(str(sig_prefix), "", *sig_prefix)
        signode += addnodes.desc_name("", "", addnodes.desc_sig_name(sig, sig))

        return sig, ""
