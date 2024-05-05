""" Parsed AST nodes.

"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Function:
    comment: str
    kind: str
    name: str
    variable_lists: list["VariableList"]


# @dataclass
# class FunctionBlock:
#     name: str


@dataclass
class Property:
    comment: str
    name: str
    ty: "Type"
    # init: Optional["Expression"]


@dataclass
class VariableList:
    kind: str
    flags: list[str]
    variables: list["Variable"]


@dataclass
class Variable:
    name: str
    address: Optional[str]
    ty: "Type"
    init: Optional["Expression"]
    comment: str


@dataclass
class TypeDef:
    comment: str
    name: str
    ty: "Type"


class Type:
    pass


@dataclass
class Struct(Type):
    fields: list["StructField"]


@dataclass
class Union(Type):
    fields: list["StructField"]


StructField = Variable


@dataclass
class Enum(Type):
    options: list["EnumOption"]
    base: Optional["Type"]


@dataclass
class EnumOption:
    name: str
    init: None


@dataclass
class LabeledArgument:
    label: str
    value: "Expression"


class Expression:
    pass


@dataclass
class Binop(Expression):
    lhs: "Expression"
    op: str
    rhs: "Expression"


@dataclass
class Unop(Expression):
    op: str
    rhs: "Expression"


@dataclass
class Call(Expression):
    callee: "Expression"
    arguments: list["Expression"]


@dataclass
class Number(Expression):
    value: int


@dataclass
class FqNameRef(Expression):
    names: str


def expression_to_text(expr, parens=False) -> str:
    if isinstance(expr, Number):
        return f"{expr.value}"
    elif isinstance(expr, FqNameRef):
        return ".".join(expr.names)
    elif isinstance(expr, Unop):
        rhs = expression_to_text(expr.rhs, parens=True)
        if parens:
            return f"({expr.op}{rhs})"
        else:
            return f"{expr.op}{rhs}"
    elif isinstance(expr, Call):
        callee = expression_to_text(expr.callee, parens=True)
        args = ",".join(expression_to_text(a) for a in expr.arguments)
        return f"{callee}({args})"
    elif isinstance(expr, Binop):
        lhs = expression_to_text(expr.lhs, parens=True)
        rhs = expression_to_text(expr.rhs, parens=True)
        if parens:
            return f"({lhs} {expr.op} {rhs})"
        else:
            return f"{lhs} {expr.op} {rhs}"
    else:
        raise NotImplementedError(f"Not impl: {expr}")


def type_to_text(ty) -> str:
    if isinstance(ty, StringType):
        if ty.size:
            size = expression_to_text(ty.size)
            return f"STRING({size})"
        else:
            return "STRING"
    elif isinstance(ty, IntegerType):
        return ty.kind
    elif isinstance(ty, FqNameRef):
        return ".".join(ty.names)
    elif isinstance(ty, ArrayType):
        ",".join(
            f"{expression_to_text(r.begin)}..{expression_to_text(r.end)}" if r else "*"
            for r in ty.ranges
        )
        d = 1  # TODO
        e = type_to_text(ty.element_type)
        return f"ARRAY [{d}] OF {e}"
    elif isinstance(ty, PointerType):
        e = type_to_text(ty.element_type)
        return f"POINTER TO {e}"
    elif isinstance(ty, ReferenceType):
        e = type_to_text(ty.element_type)
        return f"REFERENCE TO {e}"
    else:
        raise ValueError(f"Not impl: {type(ty)}")


@dataclass
class TypeRef:
    name: str


@dataclass
class StringType(Type):
    size: Optional["Expression"]


@dataclass
class IntegerType(Type):
    kind: str
    domain: Optional["Range"]


@dataclass
class ArrayType(Type):
    ranges: list[Optional["Range"]]
    element_type: "Type"


@dataclass
class PointerType(Type):
    element_type: "Type"


@dataclass
class ReferenceType(Type):
    element_type: "Type"


@dataclass
class Range:
    begin: "Expression"
    end: "Expression"
