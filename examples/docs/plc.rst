***************************
Manually Typed PLC Commands
***************************


Manually Typed PLC Functions
============================

.. plc:function:: TestTypes(a, b, c, d)

   :param UINT a:
   :param LREAL b:
   :param INT c:
   :param BOOL d:

.. plc:function:: MyAtan2(y: LREAL, x: LREAL) : LREAL

   This is a regular function.

.. plc:function:: TestArgTypes(arg1, arg2, arg3)

   :param arg1: Content Arg1
   :type arg1: HERPDERP
   :param SCHERP arg2: Content Arg2
   :param LREAL arg3: Content Arg3


Manually Typed PLC Function Blocks
==================================

.. plc:functionblock:: MyFunctionBlock(MyInput: LREAL)

.. plc:functionblock:: MyFunctionBlock2(MyInput: LREAL, MyOutput: REAL, MyInputOutput: LREAL)

.. plc:functionblock:: MyFunctionBlock3(SomeInput, OtherInput, Buffer, IsReady, HasError)

   This is a very cool function block!

   :var_in INT SomeInput: Description for SomeInput.
   :IN BOOL OtherInput: About OtherInput.
   :IN_OUT LREAL Buffer:
   :OUT BOOL IsReady: Whether it is ready.
   :OUT BOOL HasError:

.. plc:functionblock:: MyExtendedFunctionBlock

   It has a base class!

This should be a reference: :plc:funcblock:`MyFunctionBlock`.

.. plc:functionblock:: FunctionBlockWithMethod

   This is some function block.

   .. plc:method:: SomeMethod()

   .. plc:method:: FunctionBlockWithMethod.MethodWithPrefix()

.. plc:method:: ImaginedFunctionBlock.SomeMethodStandAlone()

.. plc:functionblock:: FunctionBlockWithProperty

   This function block has properties, defined in multiple ways.

   .. plc:property:: Param : LREAL

   .. plc:property:: FunctionBlockWithProperty.ParamWithPrefix : LREAL

.. plc:property:: ImaginedFunctionBlock.ParamStandAlone : LREAL


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

   .. plc:member:: \
      FaceUp
      FaceDown
