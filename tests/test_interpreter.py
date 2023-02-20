"""
Test the PLC interpreter on some TwinCAT source files.
"""

import pytest
import os

from plcdoc.interpreter import PlcInterpreter, PlcDeclaration


PLC_DIR = os.path.join(os.path.dirname(__file__), "TwinCAT PLC", "MyPLC")


@pytest.fixture()
def interpreter():
    yield PlcInterpreter()


class TestPlcInterpreter:
    FILES = [
        "POUs/PlainFunction.TcPOU",
        "POUs/RegularFunction.TcPOU",
        "POUs/PlainFunctionBlock.TcPOU",
        "POUs/FB_MyBlock.TcPOU",
        "POUs/FB_SecondBlock.TcPOU",
        "POUs/MAIN.TcPOU",
        "DUTs/E_Options.TcDUT",
    ]

    def test_files(self, interpreter):
        """Test content from files directly."""
        files = [os.path.join(PLC_DIR, file) for file in self.FILES]
        interpreter.parse_source_files(files)

        objects = [
            "PlainFunction",
            "RegularFunction",
            "PlainFunctionBlock",
            "FB_MyBlock",
            "FB_MyBlock.MyMethod",
            "FB_SecondBlock",
            "MAIN",
            "E_Options",
        ]

        for name in objects:
            try:
                interpreter.get_object(name)
            except KeyError:
                pytest.fail(f"Failed to get object `{name}` as expected")

    def test_project(self, interpreter):
        """Test loading contents through a PLC project file."""
        file = os.path.join(PLC_DIR, "MyPLC.plcproj")

        interpreter.parse_plc_project(file)
