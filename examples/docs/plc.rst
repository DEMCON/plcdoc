***************************
Manually Typed PLC Commands
***************************


Manually Typed PLC Functions
============================

.. plc:function:: MyAtan2(y: LREAL, x: LREAL) : LREAL

   This is a regular function.

.. plc:function:: TestArgTypes(arg1, arg2)

   :param arg1: Content Arg1
   :type arg1: HERPDERP
   :param SCHERP arg2: Content Arg2


Manually Typed PLC Function Blocks
==================================

.. plc:functionblock:: MyFunctionBlock(MyInput: LREAL)

.. plc:functionblock:: MyFunctionBlock2(MyInput: LREAL, MyOutput: REAL, MyInputOutput: LREAL)

.. plc:functionblock:: MyFunctionBlock3(SomeInput, OtherInput, Buffer, IsReady, HasError)

   This is a very cool function block!

   :var_in int SomeInput: Description for SomeInput.
   :IN BOOL OtherInput: About OtherInput.
   :IN_OUT LREAL Buffer:
   :OUT BOOL IsReady: Whether it is ready.
   :OUT BOOL HasError:

.. plc:functionblock:: MyExtendedFunctionBlock

   It has a base class!

This should be a reference: :plc:funcblock:`MyFunctionBlock`.


Manually Typed PLC Enums
========================

.. plc:enum:: E_Options

   I am options

.. plc:enum:: Orientation

   .. plc:enumerator:: \
      FaceUp
      FaceDown

   I am an orientation.


Manually Typed PLC Structs
==========================

.. plc:struct:: ST_MyStruct

   I have properties!

.. plc:struct:: ST_MyStruct2

   .. plc:property:: \
      FaceUp
      FaceDown
