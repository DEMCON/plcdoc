from textx import metamodel_from_file
from textx.export import model_export


if __name__ == "__main__":

    meta_model = metamodel_from_file("../plc_doc/st_declaration.tx")

    # filename = "FB_MyBlockExtended.txt"
    # filename = "FB_MyBlock.txt"
    # filename = "RegularFunction.txt"
    # filename = "MyStructure.txt"
    filename = "E_Options.txt"
    model = meta_model.model_from_file("plc/" + filename)

    model_export(model, filename + ".dot")
