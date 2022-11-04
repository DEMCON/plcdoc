from textx import metamodel_from_file
from textx.export import model_export


if __name__ == "__main__":

    meta_model = metamodel_from_file("st_declaration.tx")

    model = meta_model.model_from_file("FB_MyBlock.txt")

    model_export(model, "model.dot")
