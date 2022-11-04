import unittest
import os
from textx import metamodel_from_file
from textx.export import model_export


tests_dir = os.path.dirname(os.path.abspath(__file__))


class TestGrammar(unittest.TestCase):
    """Test the defined TextX grammar for PLC files."""

    EXPORT_MODELS = True

    FILES = [
        "FB_MyBlock.txt",
        "FB_MyBlockExtended.txt",
        "RegularFunction.txt",
        "MyStructure.txt",
        "MyStructureExtended.txt",
        "E_Options.txt",
    ]

    def setUp(self) -> None:
        txpath = os.path.realpath(tests_dir + "/../plc_doc/st_declaration.tx")
        self.meta_model = metamodel_from_file(txpath)

    def test_grammar(self):
        """Simply parse a bunch of the files.

        The main goal is no syntax errors are encountered.
        """
        for filename in self.FILES:
            filepath = os.path.realpath(tests_dir + "/plc_code/" + filename)
            model = self.meta_model.model_from_file(filepath)
            self.assertIsNotNone(model)

            if self.EXPORT_MODELS:
                exportpath = os.path.realpath(tests_dir + "/models/" + filename)
                model_export(model, exportpath)


if __name__ == "__main__":
    unittest.main()
