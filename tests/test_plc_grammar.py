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
            assert model.function is not None or model.typedefs


def test_grammar_comments(meta_model):
    """Test grammar on a file with a lot of comments.

    Some comments are important while some can be discarded.
    """
    filename = "FBWithManyComments.txt"
    filepath = os.path.realpath(tests_dir + "/plc_code/" + filename)
    try:
        model = meta_model.model_from_file(filepath)
    except:
        pytest.fail(f"Error when analyzing the file `{filename}`")
    else:
        assert model is not None
        assert model.function is not None
        assert len(model.typedefs) == 0
        fb = model.function
