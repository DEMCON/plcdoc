import os
import sys

sys.path.insert(0, os.path.abspath("."))

extensions = ["sphinx.ext.autodoc", "plcdoc"]

# The suffix of source filenames.
source_suffix = ".rst"

nitpicky = True

plc_sources = [
    # "../TwinCAT PLC/.TcPOU",
    "../../TwinCAT PLC/MyPLC/POUs/RegularFunction.TcPOU",
    "../../TwinCAT PLC/MyPLC/POUs/PlainFunctionBlock.TcPOU",
    "../../TwinCAT PLC/MyPLC/POUs/PlainFunction.TcPOU",
    "../../TwinCAT PLC/MyPLC/POUs/FB_MyBlock.TcPOU",
]
