import os
import sys

sys.path.insert(0, os.path.abspath("."))

extensions = ["plcdoc"]

# The suffix of source filenames.
source_suffix = ".rst"

nitpicky = True

plc_sources = [
    os.path.join(os.path.abspath("."), item)
    for item in ["src_plc/*.TcPOU", "src_plc/*.TcDUT"]
]
