.. TestProject documentation master file, created by
   sphinx-quickstart on Fri Nov  4 17:13:56 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TestProject's documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



Auto Typed PLC Stuff
====================

.. plc:autofunctionblock:: FB_MyBlock


Manually Typed PLC Function Blocks
==================================

.. plc:functionblock:: MyFunctionBlock2(MyInput: LREAL)

.. plc:functionblock:: MyFunctionBlock

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


Regular Python Examples
=======================

.. py:function:: my_function


.. py:function:: python_function(arg1: str) -> bool

   This is a very cool function but then in Python.

   :param str arg1: Awesome parameter.


.. py:function:: some_other_function

   :param int x:
   :param int y:
   :param int z:
   :rtype: int


.. py:class:: SomeClass(x: int)

   Bases: :py:class:`BaseClass`

   Documentation of a class

   :param x: An input

   .. py:method:: get_stuff() -> bool

      :returns: True if there is stuff

   .. py:property:: some_property

      :type: int


Above is some info about for example :py:func:`my_function`


Regular C++ Examples
====================

.. cpp:class:: MyClass : public BaseClass

   I am an inherited class

   .. cpp:function:: bool get_ready() const

.. cpp:function:: bool my_funciton(const int& x)

.. cpp:struct:: MyStruct

   I am a structure.

   .. cpp:member:: int x

   .. cpp:member:: int y
