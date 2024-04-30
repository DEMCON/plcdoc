""" 
Lark based PLC parser.
"""


from .lexer import MyLexer
from .transform import MyTransformer
from pprint import pprint
import logging
import lark

logger = logging.getLogger(__name__)


def parse_new(text: str):
    print(text)
    # for token in tokenize(text):
    #     print(token)

    tree = parser.parse(text)
    # print("PARSED", tree)
    print("PARSED:")
    pprint(tree)
    return tree


grammar = """
start: declaration EOF

declaration: function | property | type_def | variable_list

function: (KW_PROGRAM | KW_FUNCTION_BLOCK | KW_FUNCTION | KW_METHOD | KW_INTERFACE) visibility ID (COLON type)? extends? SEMI? variable_lists
property: KW_PROPERTY visibility ID COLON type
extends: KW_EXTENDS ID
visibility: (KW_ABSTRACT | KW_PUBLIC | KW_PRIVATE | KW_PROTECTED | KW_INTERNAL | KW_FINAL)?
variable_lists: variable_list*
variable_list: (KW_VAR_INPUT | KW_VAR_OUTPUT | KW_VAR_GLOBAL | KW_VAR) variable* KW_END_VAR
variable: ID COLON type initializer? SEMI

type_def: KW_TYPE ID extends? COLON (struct | union | enum) KW_END_TYPE
struct: KW_STRUCT variable* KW_END_STRUCT
union: KW_UNION variable* KW_END_UNION
enum: PARENTHESIS_OPEN enum_values PARENTHESIS_CLOSE SEMI
enum_values: enum_value
           | enum_values COMMA enum_value
enum_value: ID initializer?

initializer: COLON_EQUALS expression
labeled_arguments: labeled_argument
                 | labeled_arguments COMMA labeled_argument
labeled_argument: ID COLON_EQUALS expression

expressions: expression
           | expressions COMMA expression
expression: term
          | expression (PLUS | MINUS) term
term: factor
    | term (ASTERIX | SLASH) factor
factor: atom
atom: literal
    | name_ref
    | struct_literal
    | range_literal
    | PARENTHESIS_OPEN expression PARENTHESIS_CLOSE
name_ref: ID
struct_literal: PARENTHESIS_OPEN labeled_arguments PARENTHESIS_CLOSE
range_literal: PARENTHESIS_OPEN expression DOTDOT expression PARENTHESIS_CLOSE
literal: NUMBER
       | REAL
       | BIN_NUMBER
       | OCT_NUMBER
       | HEX_NUMBER
       | STRING

type: name_ref
    | string_type
    | array_type
    | pointer_type
    | reference_type
string_type: KW_STRING
           | KW_STRING PARENTHESIS_OPEN expression PARENTHESIS_CLOSE
           | KW_STRING BRACKET_OPEN expression BRACKET_CLOSE
array_type: KW_ARRAY BRACKET_OPEN subranges BRACKET_CLOSE KW_OF type
pointer_type: KW_POINTER KW_TO ID
reference_type: KW_REFERENCE KW_TO ID

subranges: subrange
         | subranges COMMA subrange
subrange: ASTERIX
        | expression DOTDOT expression

%declare KW_ABSTRACT
%declare KW_PROGRAM
%declare KW_FUNCTION
%declare KW_FUNCTION_BLOCK
%declare KW_INTERFACE
%declare KW_METHOD
%declare KW_PROPERTY
%declare KW_EXTENDS
%declare KW_FINAL
%declare KW_PUBLIC
%declare KW_PRIVATE
%declare KW_PROTECTED
%declare KW_INTERNAL
%declare KW_TYPE
%declare KW_END_TYPE
%declare KW_POINTER
%declare KW_STRUCT
%declare KW_END_STRUCT
%declare KW_UNION
%declare KW_END_UNION
%declare KW_STRING
%declare KW_ARRAY
%declare KW_OF
%declare KW_REFERENCE
%declare KW_TO
%declare KW_VAR_GLOBAL
%declare KW_VAR_INPUT
%declare KW_VAR_OUTPUT
%declare KW_VAR
%declare KW_END_VAR

%declare ID
%declare NUMBER REAL BIN_NUMBER OCT_NUMBER HEX_NUMBER
%declare STRING
%declare COLON_EQUALS
%declare COLON SEMI COMMA DOT DOTDOT
%declare PLUS MINUS ASTERIX SLASH
%declare BRACE_OPEN BRACE_CLOSE
%declare PARENTHESIS_OPEN PARENTHESIS_CLOSE
%declare BRACKET_OPEN BRACKET_CLOSE
%declare EOF

"""

parser = lark.Lark(grammar, parser="lalr", transformer=MyTransformer(), lexer=MyLexer)
