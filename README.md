# PLC Sphinx Parser

[![Documentation Status](https://readthedocs.org/projects/plc-doc/badge/?version=latest)](https://plc-doc.readthedocs.io/latest/?badge=latest)
[![Unit tests](https://github.com/DEMCON/plcdoc/actions/workflows/tests.yml/badge.svg)](https://github.com/DEMCON/plcdoc/actions)
[![codecov](https://codecov.io/gh/DEMCON/plcdoc/graph/badge.svg?token=xMg0U6mX2r)](https://codecov.io/gh/DEMCON/plcdoc)

This is a work-in-progress of a tool to get documentation with Sphinx from TwinCAT PLC.
The focus is on PLC code made with Structured Text (ST), i.e. the IEC 61131-3 standard.

At the basis is the [TextX](https://github.com/textX/textX) package to parse some of the PLC code.

This package allows for recognition of ST code such that definitions can be manually typed in.
More useful however is the feature to automatically parse declarations from ST and insert the results in your Sphinx
document.

## Why

TwinCAT has a built-in documentation system. However, it is only semi-official and it cannot be exported to stand-alone
documents. Currently it is common to write your program documentation externally and attach it with your source. The 
downsides of this approach are clear: structural or name changes must all be done twice, which can be easily forgotten.

It would be ideal to, like with many modern languages, produce from-source documentation on the fly with continuous 
integration. This way you can focus exclusively on your code while up-to-date docs are always available.

## How to use

**Warning:** `plcdoc` is still in development and although some documentation can be made, you will likely run into many warnings and errors.

### Install

Install from [pypi.org](https://pypi.org/project/plcdoc/) with:
```
pip install plcdoc
```

### Configuration

In your `conf.py`, add the extension:

```python
extensions = ["plcdoc"]
```

For automatic source parsing, either list your PLC source files:

```python
plc_sources = [
    "path/to/file1.TcPOU",
    # ...
]
```

And/or list a project file directly:

```python
plc_project = "path/to/project.plcproj"
```

When using a project file it will be scoured for listed sources and those sources will be included directly.

### Manual typing

You define Structured Text objects like so:

```rst
.. plc:function:: MyFunction(myFloat, myInt) : BOOL

   :param REAL myFloat: First variable
   :param UDINT myInt:  Second variable, very important

   This is the general description.
```

### Auto typing

You can insert in-source definitions like this:

```rst
.. plc:autofunction MyFunction
```

### Structured Text doc comments

Follow the [Beckhoff comment style](https://infosys.beckhoff.com/english.php?content=../content/1033/tc3_plc_intro/6158078987.html&id=)
to allow parsing from source. Fortunately, this is close to e.g. the Python style of doc comments.

For example, the declaration to make the `plc:autofunction` above give the same result as the `plc:function` could be:

```
(*
This is the general description.
*)
FUNCTION MyFunction : BOOL
VAR_INPUT
    myFloat         : REAL;        // First variable
    myInt           : UDINT;       // Second variable, very important
VAR_END
```

Types, arguments, etc. are deduced from the source code itself and corresponding comments are put alongside.

## Possibilities and limitations

The goal is that all code inside `<Declaration></Declaration>` tags can be parsed. Everything outside, e.g. inside
`<Definition></Definition>` tags, cannot and will be ignored.

Although all common notations should be supported, due to the flexibility of Structured Text (and any programming
languages in general), there will be cases where source parsing fails. It is recommended to set up docs generation
early on to identify failures quickly.

The biggest source of errors inside declarations is initial expressions. For example, a variable could be initialized 
as a sum, involving other variables, and include various literal notations. This is hard to capture in full.

## Developing

### Setup

Get the development tools and make your installation editable by running:
```
pip install -e .[test,doc]
```

### Tests

Run all tests with `python -m pytest`.

The structure is based on the Sphinx unittest principle. There are actual doc roots present which are processed as 
normal during a test.

Run with coverage with `python -m pytest --cov`. Add `--cov-report=html` to produce an HTML test report.

### Basis and inspirations

There are a bunch of projects linking new languages to Sphinx:

 * C++: https://github.com/breathe-doc/breathe (language, typing and auto-doc)
 * MATLAB: https://github.com/sphinx-contrib/matlabdomain (language, typing and auto-doc)
 * JavaScript: https://github.com/mozilla/sphinx-js (language, typing and auto-doc)
 * Python (`autodoc`): https://github.com/sphinx-doc/sphinx/tree/master/sphinx/ext/autodoc (auto-doc)

`breathe` is the biggest and most complete, but very abstract. `sphinxcontrib-matlabdomain` was the main inspiration for
the package layout. The auto-documentation however mimics the default Python `autodoc` extension very closely.

## References

Other useful projects: 

 * [TcTools](https://github.com/DEMCON/twincat-tools):
   * A package with helper tools for developing TwinCAT PLC code (also made by us).
 * [Blark](https://github.com/klauer/blark):
   * Parsing of PLC Structured Text code in Python using Lark.  
     Very impressive and much more complete than the PLC parsing done here, but slight overkill for the purpose here.
 * [TcBlack](https://github.com/Roald87/TcBlack):
   * Black-inspired formatting tool for PLC Structured Text.
