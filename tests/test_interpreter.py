"""
Test the PLC interpreter on some TwinCAT source files.
"""

import pytest
import os

from plcdoc.interpreter import PlcInterpreter, PlcDeclaration


PLC_DIR = os.path.join(os.path.dirname(__file__), "TwinCAT PLC", "MyPLC")


class TestPlcInterpreter:
    FILES = [
        "POUs/PlainFunction.TcPOU",
        "POUs/RegularFunction.TcPOU",
        "POUs/PlainFunctionBlock.TcPOU",
        "POUs/FB_MyBlock.TcPOU",
        "POUs/FB_SecondBlock.TcPOU",
    ]

    def test_init(self):
        files = [os.path.join(PLC_DIR, file) for file in self.FILES]
        interpreter = PlcInterpreter(files)

        objects = ["PlainFunction", "FB_MyBlock", "FB_MyBlock.MyMethod"]

        for name in objects:
            try:
                interpreter.get_object(name)
            except:
                pytest.fail(f"Failed to get object `{name}` as expected")
