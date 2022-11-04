import xml.etree.ElementTree as ET
from textx import metamodel_from_file


def parse_file(path: str):
    tree = ET.parse(path)
    root = tree.getroot()

    model = metamodel_from_file("plc_doc/st_declaration.tx")

    for item in root:
        plc_item = item.tag
        name = item.attrib["Name"]

        node_declaration = item.find("Declaration")
        # print(node_declaration.text)

        method_nodes = item.findall("Method")
        for method_node in method_nodes:
            method_declaration = method_node.find("Declaration")
            # print(method_declaration.text)


if __name__ == "__main__":
    parse_file("examples/FB_MyBlock.TcPOU")
