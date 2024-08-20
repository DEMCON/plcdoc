
.. Functions -----------------------------

.. plc:function:: BoringFunction(y: LREAL, x: LREAL) : LREAL

   Get the 4-quadrant arctan of a coordinates.

   :param y: Y-coordinate
   :param x: X-coordinate
   :returns: Angle in radians


.. Function Blocks -----------------------------

.. plc:functionblock:: FB_TypedByHand(SomeInput, OtherInput, Buffer, IsReady, HasError)

   This is a very cool function block!

   :var_in LREAL SomeInput: Description for SomeInput.
   :IN BOOL OtherInput: About OtherInput.
   :IN_OUT Buffer:
   :var_in_out_type Buffer: LREAL
   :OUT BOOL IsReady: Whether it is ready.
   :OUT BOOL HasError:

.. plc:functionblock:: FunctionBlockWithMethod

   .. plc:method:: SomeMethod()

   .. plc:method:: FunctionBlockWithMethod.MethodWithPrefix()

.. plc:method:: FunctionBlockWithMethod.SomeMethodStandAlone()


.. Enums -----------------------------

.. plc:enum:: E_Options

   I am options

.. plc:enum:: Orientation

   .. plc:enumerator:: \
      FaceUp
      FaceDown

   I am an orientation.


.. Structs -----------------------------

.. plc:struct:: ST_MyStruct

   I have properties!

.. plc:struct:: ST_MyStruct2

   .. plc:property:: \
      FaceUp
      FaceDown


.. GVL -----------------------------

.. plc:gvl:: GVL_MyList

   :var LREAL my_double: Some double-type variable
   :var USINT some_int: My short integer
