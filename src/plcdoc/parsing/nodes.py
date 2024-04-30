""" Parsed AST nodes.

"""

from typing import Optional, Any, Union
from dataclasses import dataclass


@dataclass
class Function:
    comment1: str
    kind: str
    name: str
    variable_lists: list["VariableList"]


# @dataclass
# class FunctionBlock:
#     name: str

@dataclass
class Property:
    name: str
    ty: "Type"
    # init: Optional["Expression"]

@dataclass
class VariableList:
    kind: str
    variables: list["Variable"]


@dataclass
class Variable:
    name: str
    ty: "Type"
    init: Optional["Expression"]


@dataclass
class TypeDef:
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
class Number(Expression):
    value: int


@dataclass
class NameRef(Expression):
    name: str


@dataclass
class TypeRef:
    name: str

@dataclass
class Array:
    ranges: list["Range"]
    element_type: "Type"

@dataclass
class Range:
    begin: "Expression"
    end: "Expression"
