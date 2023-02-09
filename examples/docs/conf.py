# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "TestProject"
copyright = "2022, Robert Roos"
author = "Robert Roos"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["plcdoc", "sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

plc_sources = [
    # "../TwinCAT PLC/.TcPOU",
    "../TwinCAT PLC/MyPLC/POUs/RegularFunction.TcPOU",
    "../TwinCAT PLC/MyPLC/POUs/PlainFunctionBlock.TcPOU",
    "../TwinCAT PLC/MyPLC/POUs/PlainFunction.TcPOU",
    "../TwinCAT PLC/MyPLC/POUs/FB_MyBlock.TcPOU",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
