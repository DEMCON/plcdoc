import lark
from . import nodes as ast


class MyTransformer(lark.Transformer):
    def start(self, rhs):
        return rhs[0]

    def declaration(self, rhs):
        return rhs[0]

    def visibility(self, rhs):
        return 1

    def function(self, rhs):
        comment1 = rhs[0].value.comment1
        print("FUNC", rhs)
        kind = rhs[0].value.text.lower().replace("_", "")
        index = 1
        if isinstance(rhs[index], int):
            index += 1
        name = rhs[index].value.text
        variable_lists = rhs[-1]
        return ast.Function(comment1, kind, name, variable_lists)

    def property(self, rhs):
        name = rhs[2].value.text
        ty = rhs[4]
        return ast.Property(name, ty)

    def type_def(self, rhs):
        name = rhs[1].value.text
        ty = rhs[-2]
        return ast.TypeDef(name, ty)

    def enum(self, rhs):
        options = rhs[1]
        return ast.Enum(options)

    def enum_values(self, rhs):
        return comma(rhs)

    def enum_value(self, rhs):
        name = rhs[0].value.text
        if len(rhs) > 1:
            init = rhs[1]
        else:
            init = None
        return ast.EnumOption(name, init)

    def struct(self, rhs):
        fields = rhs[1:-1]
        return ast.Struct(fields)

    def union(self, rhs):
        fields = rhs[1:-1]
        return ast.Union(fields)

    def variable_lists(self, rhs):
        return rhs

    def variable_list(self, rhs):
        kind = rhs[0].value.text
        variables = rhs[1:-1]
        return ast.VariableList(kind, variables)

    def variable(self, rhs):
        name = rhs[0].value.text
        ty = rhs[2]
        if len(rhs) > 4:
            init = rhs[3]
        else:
            init = None
        return ast.Variable(name, ty, init)

    def initializer(self, rhs):
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
        return binop(rhs)

    def term(self, rhs):
        return binop(rhs)

    def atom(self, rhs):
        if len(rhs) == 1:
            return rhs[0]
        else:
            assert len(rhs) == 3
            return rhs[1]

    def literal(self, rhs):
        value = rhs[0].value.text
        return ast.Number(value)
    
    def struct_literal(self, rhs):
        return rhs[1]
    
    def range_literal(self, rhs):
        begin = rhs[1]
        end = rhs[3]
        return ast.Range(begin, end)

    def name_ref(self, rhs):
        name = rhs[0].value.text
        return ast.NameRef(name)

    def type(self, rhs):
        return rhs[0]

    def string_type(self, rhs):
        name = rhs[0].value.text
        return ast.TypeRef(name)

    def array_type(self, rhs):
        ranges = rhs[2]
        element_type = rhs[5]
        return ast.Array(ranges, element_type)

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
