"""
Test the PLC interpreter on some TwinCAT source files.
"""

import pytest
import os

from plcdoc.interpreter import PlcInterpreter, PlcDeclaration


CODE_DIR = os.path.join(os.path.dirname(__file__), "plc_code")


@pytest.fixture()
def interpreter():
    return PlcInterpreter()


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
        files = [os.path.join(CODE_DIR, "TwinCAT PLC", "MyPLC", file) for file in self.FILES]
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
        file = os.path.join(CODE_DIR, "TwinCAT PLC", "MyPLC", "MyPLC.plcproj")
        result = interpreter.parse_plc_project(file)
        assert result

    def test_large_external_projects(self):
        """Test grammar on a big existing project.

        The goal is not so much to check the results in detail but just to make sure there are no
        errors, and we likely covered all possible syntax.

        Do not use the `interpreter` fixture as we want the object fresh each time.
        """
        projects = {
            "extern/lcls-twincat-general/LCLSGeneral/LCLSGeneral/LCLSGeneral.plcproj": (33, ),
            # "extern/lcls-twincat-motion/lcls-twincat-motion/Library/Library.plcproj": (),
        }
        # TODO: Verify output of these projects - maybe interpreter is just empty?
        for project, expected in projects.items():
            interpreter = PlcInterpreter()
            file = os.path.join(CODE_DIR, project)
            file = os.path.realpath(file)
            result = interpreter.parse_plc_project(file)
            assert result
            assert len(interpreter._models["functionblock"]) == expected[0]
