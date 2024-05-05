import lark
from . import nodes as ast


class MyTransformer(lark.Transformer):
    def start(self, rhs):
        # TODO: we can have multiple declarations
        # For example VAR_GLOBAL ..  VAR_GLOBAL CONSTANT
        return rhs[0]

    def declaration(self, rhs):
        return rhs[0]

    def visibility(self, rhs):
        return 1

    def function(self, rhs):
        # print("FUNC", rhs)
        comment, kind = rhs[0]
        name = rhs[2].value.text
        variable_lists = rhs[-1]
        return ast.Function(
            comment=comment, kind=kind, name=name, variable_lists=variable_lists
        )

    def function_kind(self, rhs):
        comment = rhs[0].value.comment1
        kind = rhs[0].value.text.lower().replace("_", "")
        return comment, kind

    def property(self, rhs):
        comment = rhs[0].value.comment1
        name = rhs[2].value.text
        ty = rhs[4]
        return ast.Property(comment, name, ty)

    def type_def(self, rhs):
        comment = rhs[0].value.comment1
        name = rhs[1].value.text
        ty = rhs[-2]
        return ast.TypeDef(comment=comment, name=name, ty=ty)

    def enum_decl(self, rhs):
        options = rhs[1]
        base = rhs[-2] if len(rhs) == 5 else None
        return ast.Enum(options, base)

    def enum_values(self, rhs):
        return comma(rhs)

    def enum_value(self, rhs):
        name = rhs[0].value.text
        init = rhs[1]
        return ast.EnumOption(name, init)

    def struct_decl(self, rhs):
        fields = rhs[1:-1]
        return ast.Struct(fields)

    def union_decl(self, rhs):
        fields = rhs[1:-1]
        return ast.Union(fields)

    def variable_lists(self, rhs):
        return rhs

    def variable_list(self, rhs):
        kind = rhs[0].value.text
        flags = rhs[1]
        variables = rhs[2:-1]
        return ast.VariableList(kind, flags, variables)

    def variable_list_flags(self, rhs):
        return [r.value.text for r in rhs]

    def variable(self, rhs):
        # print("VAR", rhs)
        names = rhs[0]
        name = names[0]
        # TODO: support more than 1 name?
        address = rhs[1]
        ty, init = rhs[3]
        comment = rhs[-1].value.comment1
        return ast.Variable(name, address, ty, init, comment)

    def variable_type_init(self, rhs):
        ty = rhs[0]
        if len(rhs) == 2:
            init = rhs[1]
        elif len(rhs) == 3:
            init = None
        else:
            init = rhs[2]
        return (ty, init)

    def address(self, rhs):
        if len(rhs) == 2:
            return rhs[1].value.text

    def initializer(self, rhs):
        if len(rhs) == 2:
            return rhs[1]

    def labeled_arguments(self, rhs):
        return comma(rhs)

    def labeled_argument(self, rhs):
        label = rhs[0].value.text
        value = rhs[2]
        return ast.LabeledArgument(label, value)

    def expressions(self, rhs):
        return comma(rhs)

    def expression(self, rhs):
        return rhs[0]

    def sum(self, rhs):
        return binop(rhs)

    def term(self, rhs):
        return binop(rhs)

    def factor(self, rhs):
        if len(rhs) == 1:
            return rhs[0]
        else:
            op = rhs[0].value.text
            return ast.Unop(op, rhs[1])

    def atom(self, rhs):
        if len(rhs) == 1:
            return rhs[0]
        elif len(rhs) == 3:
            return rhs[1]
        else:
            assert len(rhs) == 4
            callee = rhs[0]
            args = rhs[2]
            return ast.Call(callee, args)

    def literal(self, rhs):
        value = rhs[0].value.text
        return ast.Number(value)

    def struct_literal(self, rhs):
        return rhs[1]

    def range_literal(self, rhs):
        begin = rhs[1]
        end = rhs[3]
        return ast.Range(begin, end)

    def ids(self, rhs):
        if len(rhs) == 1:
            name = rhs[0].value.text
            names = [name]
        else:
            name = rhs[2].value.text
            names = rhs[0] + [name]
        return names

    def fq_name_ref(self, rhs):
        if len(rhs) == 1:
            name = rhs[0].value.text
            names = [name]
        else:
            name = rhs[2].value.text
            names = rhs[0].names + [name]
        return ast.FqNameRef(names)

    def type(self, rhs):
        # TODO: handle range indicator for integer types.
        return rhs[0]

    def integer_type(self, rhs):
        ty = rhs[0].value.text
        domain = rhs[1] if len(rhs) > 1 else None
        return ast.IntegerType(ty, domain)

    def string_type(self, rhs):
        size = rhs[2] if len(rhs) == 4 else None
        return ast.StringType(size)

    def pointer_type(self, rhs):
        ty = rhs[-1]
        return ast.PointerType(ty)

    def reference_type(self, rhs):
        ty = rhs[-1]
        return ast.ReferenceType(ty)

    def array_type(self, rhs):
        ranges = rhs[2]
        element_type = rhs[5]
        return ast.ArrayType(ranges, element_type)

    def subranges(self, rhs):
        return comma(rhs)

    def subrange(self, rhs):
        if len(rhs) == 1:
            return None
        else:
            begin = rhs[0]
            end = rhs[2]
            return ast.Range(begin, end)


def binop(rhs) -> ast.Binop:
    if len(rhs) == 1:
        return rhs[0]
    else:
        assert len(rhs) == 3
        lhs = rhs[0]
        op = rhs[1].value.text
        rhs = rhs[2]
        return ast.Binop(lhs, op, rhs)


def comma(rhs):
    """Handle a rule with one or more items, seperated by commas"""
    if len(rhs) == 1:
        return [rhs[0]]
    else:
        return rhs[0] + [rhs[2]]
