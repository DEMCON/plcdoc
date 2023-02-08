***************************
Manually Typed PLC Commands
***************************

Manually Typed PLC Function Blocks
==================================

.. plc:functionblock:: MyFunctionBlock2(MyInput: LREAL)

.. plc:functionblock:: MyFunctionBlock3(MyInput: LREAL, MyOutput: REAL, MyInputOutput: LREAL)

.. plc:functionblock:: MyFunctionBlock(SomeInput, OtherInput, Buffer, IsReady, HasError)

   This is a very cool function block!

   :var_in int SomeInput: Description for SomeInput.
   :IN BOOL OtherInput: About OtherInput.
   :IN_OUT LREAL Buffer:
   :OUT BOOL IsReady: Whether it is ready.
   :OUT BOOL HasError:

.. plc:functionblock:: MyExtendedFunctionBlock

   It has a base class!

.. plc:function:: MyAtan2(y: LREAL, x: LREAL) : LREAL

   This is a regular function.

This should be a reference :plc:funcblock:`FirstFunction`.


Manually Typed PLC Functions
============================

.. plc:function:: MyAtan2(y: LREAL, x: LREAL) : LREAL

   This is a regular function.


Manually Typed PLC Enums
========================

.. plc:enum:: E_Options

   I am options

.. plc:enum:: Orientation

   .. plc:enumerator:: \
      FaceUp
      FaceDown


Manually Typed PLC Structs
==========================

.. plc:struct:: ST_MyStruct

   I have properties!

.. plc:struct:: ST_MyStruct2

   .. plc:property:: \
      FaceUp
      FaceDown
