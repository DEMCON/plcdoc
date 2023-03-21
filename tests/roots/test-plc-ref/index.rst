
.. plc:function:: MyFunction

This is a reference to :plc:func:`MyFunction`.

This is an invalid reference: :plc:func:`IDontExist`.

.. plc:functionblock:: MyBlock

This is a reference to :plc:funcblock:`MyBlock`.

This is an invalid reference: :plc:func:`DoesNotExistEither`.


Now test using custom types in argument or return types, in either notation:

.. plc:functionblock:: BlockReturn

.. plc:functionblock:: BlockArg

.. plc:function:: FunctionWithMyBlockSignature(x: BlockArg) : BlockReturn


.. plc:function:: FunctionWithMyBlockList(x)

   :param x:
   :type x: BlockArg
   :rtype: BlockReturn
