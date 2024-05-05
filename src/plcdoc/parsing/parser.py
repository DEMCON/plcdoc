"""
Lark based PLC parser.
"""

from .lexer import MyLexer
from .transform import MyTransformer
import logging
import lark

logger = logging.getLogger(__name__)


def parse_new(text: str):
    # print(text)
    tree = parser.parse(text)
    # print("PARSED:")
    # pprint(tree, width=150)
    return tree


grammar = """
start: declaration+ EOF

declaration: function | property | type_def | variable_list

function: function_kind visibility ID (COLON type)? exim SEMI? variable_lists
function_kind: KW_PROGRAM
             | KW_FUNCTION_BLOCK
             | KW_FUNCTION
             | KW_METHOD
             | KW_INTERFACE
property: KW_PROPERTY visibility ID COLON type
exim: extends implements?
extends: (KW_EXTENDS fq_name_ref)?
implements: KW_IMPLEMENTS fq_name_ref
visibility: (KW_ABSTRACT | KW_ACCESS | KW_FINAL)?
variable_lists: variable_list*
variable_list: KW_VAR variable_list_flags variable* KW_END_VAR
variable_list_flags: (KW_CONSTANT | KW_PERSISTENT)*
variable: ids address COLON variable_type_init SEMI
variable_type_init: type initializer
                  | type PARENTHESIS_OPEN labeled_arguments PARENTHESIS_CLOSE
                  | type PARENTHESIS_OPEN expressions PARENTHESIS_CLOSE
                  | type PARENTHESIS_OPEN PARENTHESIS_CLOSE
address: (KW_AT ADDR)?

type_def: KW_TYPE ID extends COLON (struct_decl | union_decl | enum_decl) KW_END_TYPE
struct_decl: KW_STRUCT variable* KW_END_STRUCT
union_decl: KW_UNION variable* KW_END_UNION
enum_decl: PARENTHESIS_OPEN enum_values PARENTHESIS_CLOSE integer_type? SEMI
enum_values: enum_value
           | enum_values COMMA enum_value
enum_value: ID initializer

initializer: (COLON_EQUALS expression)?
labeled_arguments: labeled_argument
                 | labeled_arguments COMMA labeled_argument
labeled_argument: ID COLON_EQUALS expression

expressions: expression
           | expressions COMMA expression

expression: sum
sum: term
          | expression (PLUS | MINUS) term
term: factor
    | term (ASTERIX | SLASH) factor
factor: atom
      | MINUS factor
atom: literal
    | fq_name_ref
    | struct_literal
    | range_literal
    | PARENTHESIS_OPEN expression PARENTHESIS_CLOSE
    | atom PARENTHESIS_OPEN expressions PARENTHESIS_CLOSE

ids: ID
   | ids COMMA ID
fq_name_ref: ID
           | fq_name_ref DOT ID

struct_literal: PARENTHESIS_OPEN labeled_arguments PARENTHESIS_CLOSE
range_literal: PARENTHESIS_OPEN expression DOTDOT expression PARENTHESIS_CLOSE
literal: NUMBER
       | REAL
       | TIME
       | STRING

type: fq_name_ref
    | integer_type
    | string_type
    | array_type
    | pointer_type
    | reference_type
integer_type: INTTYPE range_literal?
string_type: (KW_STRING | KW_WSTRING)
           | (KW_STRING | KW_WSTRING) PARENTHESIS_OPEN expression PARENTHESIS_CLOSE
           | (KW_STRING | KW_WSTRING) BRACKET_OPEN expression BRACKET_CLOSE
pointer_type: KW_POINTER KW_TO type
reference_type: KW_REFERENCE KW_TO type
array_type: KW_ARRAY BRACKET_OPEN subranges BRACKET_CLOSE KW_OF type
subranges: subrange
         | subranges COMMA subrange
subrange: ASTERIX
        | expression DOTDOT expression

%declare KW_ABSTRACT
%declare KW_ARRAY
%declare KW_ACCESS
%declare KW_AT
%declare KW_CONSTANT
%declare KW_END_STRUCT
%declare KW_END_TYPE
%declare KW_END_UNION
%declare KW_END_VAR
%declare KW_EXTENDS
%declare KW_FINAL
%declare KW_FUNCTION
%declare KW_FUNCTION_BLOCK
%declare KW_IMPLEMENTS
%declare KW_INTERFACE
%declare KW_METHOD
%declare KW_OF
%declare KW_PERSISTENT
%declare KW_PROPERTY
%declare KW_PROGRAM
%declare KW_POINTER
%declare KW_STRUCT
%declare KW_REFERENCE
%declare KW_STRING
%declare KW_TO
%declare KW_TYPE
%declare KW_UNION
%declare KW_VAR
%declare KW_WSTRING

%declare ID
%declare NUMBER REAL
%declare TIME ADDR
%declare STRING INTTYPE
%declare COLON_EQUALS
%declare COLON SEMI COMMA DOT DOTDOT
%declare PLUS MINUS ASTERIX SLASH
%declare BRACE_OPEN BRACE_CLOSE
%declare PARENTHESIS_OPEN PARENTHESIS_CLOSE
%declare BRACKET_OPEN BRACKET_CLOSE
%declare EOF

"""

parser = lark.Lark(grammar, parser="lalr", transformer=MyTransformer(), lexer=MyLexer)
