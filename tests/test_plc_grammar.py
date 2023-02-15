"""
Run the TextX grammar over some PLC code to see if it works.
"""

import pytest

import os
from textx import metamodel_from_file


tests_dir = os.path.dirname(os.path.abspath(__file__))


def test_grammar_on_files():
    txpath = os.path.realpath(tests_dir + "/../plcdoc/st_declaration.tx")
    meta_model = metamodel_from_file(txpath)

    files = [
        "FB_MyBlock.txt",
        "FB_MyBlockExtended.txt",
        "RegularFunction.txt",
        "MyStructure.txt",
        "MyStructureExtended.txt",
        "E_Options.txt",
        "Main.txt"
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
