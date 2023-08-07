"""
Run the TextX grammar over some PLC code to see if it works.
"""

import pytest

import os
from textx import metamodel_from_file


tests_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture()
def meta_model():
    txpath = os.path.realpath(tests_dir + "/../plcdoc/st_declaration.tx")
    return metamodel_from_file(txpath)


def test_grammar_on_files(meta_model):
    """Test if a range of files can all be parsed without errors."""
    files = [
        "FB_MyBlock.txt",
        "FB_MyBlockExtended.txt",
        "RegularFunction.txt",
        "MyStructure.txt",
        "MyStructureExtended.txt",
        "E_Options.txt",
        "E_Filter.txt",
        "Main.txt",
    ]

    for filename in files:
        filepath = os.path.realpath(tests_dir + "/plc_code/" + filename)
        try:
            model = meta_model.model_from_file(filepath)
        except:
            pytest.fail(f"Error when analyzing the file `{filename}`")
        else:
            assert model is not None
            assert model.functions or model.types


def assert_variable(var, expected):
    assert var.name == expected[0] and var.type.name == expected[1]

    if isinstance(expected[2], dict):
        for i, (key, value) in enumerate(expected[2].items()):
            assert var.value.fields[i].name == key
            assert var.value.fields[i].value == value
    else:
        assert var.value == expected[2]

    if isinstance(expected[3], list):
        assert len(var.arglist.fields) == len(expected[3])
        for i, value in enumerate(expected[3]):
            assert var.arglist.fields[i].name == ""
            assert var.arglist.fields[i].value == value
    elif isinstance(expected[3], dict):
        assert len(var.arglist.fields) == len(expected[3])
        for i, (key, value) in enumerate(expected[3].items()):
            assert var.arglist.fields[i].name == key
            assert var.arglist.fields[i].value == value
    else:
        assert var.arglist is None

    assert var.type.array == expected[4]

    if expected[5]:
        assert var.type.pointer == expected[5]
    else:
        assert not var.type.pointer


def test_grammar_variables(meta_model):
    """Test variables in declarations specifically.

    PLC can create different variables in different ways, test all of them here.
    """
    filename = "FB_Variables.txt"
    filepath = os.path.realpath(tests_dir + "/plc_code/" + filename)
    try:
        model = meta_model.model_from_file(filepath)
    except:
        pytest.fail(f"Error when analyzing the file `{filename}`")
    else:
        assert model.functions
        fb = model.functions[0]
        assert fb.lists
        variables = fb.lists[0].variables

        expected_list = [
            # (Name, BaseType, Value, ArgList, Array, Pointer)
            ("myfloat_no_ws", "REAL", None, None, None, None),
            ("myfloat", "REAL", None, None, None, None),

            ("mydoubleinit1", "LREAL", 1.0, None, None, None),
            ("mydoubleinit2", "LREAL", 1.0, None, None, None),
            ("myinteger", "SINT", 420, None, None, None),
            ("mystring", "STRING", "test", None, None, None),

            ("my_object", "MyObject", None, [], None, None),
            ("my_object1", "MyObject", None, [7], None, None),
            ("my_object2", "MyObject", None, ["hi", 23, "FALSE"], None, None),
            ("my_object3", "MyObject", None, {"text": "hi", "number": 23, "flag": "FALSE"}, None, None),
            ("my_object4", "MyObject", None, {"text": "hi", "number": 23, "flag": "FALSE"}, None, None),
            ("mystring_size1", "STRING", None, [15], None, None),
            ("mystring_size2", "STRING", None, [17], None, None),

            ("myint", "INT", "SomeConstant", None, None, None),
            ("myint2", "INT", "E_Error.NoError", None, None, None),

            ("mylist", "BOOL", None, None, "0..4", None),
            ("mylist_ws", "BOOL", None, None, "0..4", None),
            ("mylist_var_idx", "BOOL", None, None, "Idx.start..Idx.end", None),
            ("mylist_sum", "BOOL", None, None, "0..MAX-1", None),
            ("mylist_multi", "BOOL", None, None, "1..10,1..10", None),
            ("mylist_multi2", "BOOL", None, None, "1..10,1..10", None),
            ("mylist_dyn", "BOOL", None, None, "*", None),
            ("mylist_dyn_multi", "BOOL", None, None, "*,*,*", None),

            ("mystruct", "MyStruct", None, [], None, None),
            ("mystruct2", "MyStruct", {"number": 1.0, "text": "hi"}, None, None, None),

            ("specialint1", "UDINT", "2#1001_0110", None, None, None),
            ("specialint2", "UDINT", "8#67", None, None, None),
            ("specialint3", "UDINT", "16#FF_FF_FF", None, None, None),
            ("specialint4", "UDINT", "UDINT#16#1", None, None, None),
            ("specialint5", "UDINT", "1_000_000", None, None, None),

            ("mypointer1", "UDINT", None, None, None, "POINTER"),
            ("mypointer2", "UDINT", None, None, None, "REFERENCE"),

            ("timeout1", "TIME", "T#2S", None, None, None),
            ("timeout2", "TIME", "T#12m13s14ms", None, None, None),
        ]

        # TODO: Test arithmetic in expressions

        assert len(variables) == 34

        for i, expected in enumerate(expected_list):
            assert_variable(variables[i], expected)


def test_grammar_comments(meta_model):
    """Test grammar on a file with a lot of comments.

    Some comments are important while some can be discarded.
    """
    filename = "FB_Comments.txt"
    filepath = os.path.realpath(tests_dir + "/plc_code/" + filename)
    try:
        model = meta_model.model_from_file(filepath)
    except:
        pytest.fail(f"Error when analyzing the file `{filename}`")
    else:
        assert model is not None
        assert model.functions and not model.types
        fb = model.functions[0]

        # Make sure the real code came through properly:
        assert fb.name == "FB_MyBlock" and fb.function_type == "FUNCTION_BLOCK"
        assert len(fb.lists) == 4 and \
               [l.name for l in fb.lists] == ["VAR_INPUT", "VAR_OUTPUT", "VAR", "VAR"]
        assert [l.constant for l in fb.lists] == [False, False, True, False]

        # All the fields containing a doc-comment:
        list_important = [
            fb.comments[-1].text,
            fb.lists[0].variables[0].comment.text,
            fb.lists[0].variables[1].comment.text,
            fb.lists[1].variables[0].comment.text,
            fb.lists[2].variables[0].comment.text,
            fb.lists[3].variables[0].comment.text,
        ]

        for comment in list_important:
            assert "Important" in comment and "Ignored" not in comment
        # We don't verify the content of ignored comments, they might dissappear in the future

        # Check attribute came over:
        attributes = [c for c in fb.comments if type(c).__name__ == "Attribute"]
        assert len(attributes) == 1 and attributes[0].name == "naming"


# Also see `test_large_external_projects` for more massive tests
