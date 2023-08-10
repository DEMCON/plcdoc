##########
Directives
##########

.. default-domain:: plc

.. note:: All ``plc:`` domain prefixes are omitted here.

function
========

.. code-block:: rst

   .. function:: <signature>
      :var_in <type> <name>:
      :var_out <type> <name>:
      :var_in_out <type> <name>:
      :var_in <type> <name>:
      :returnvalue:
      :returntype:

Examples
--------

Take in a function name with real signature:

.. code-block:: rst

   .. function:: Atan2(y: LREAL, x: LREAL) : LREAL

      Get 4-quadrant arc-tangent in degrees.

.. function:: Atan2(y: LREAL, x: LREAL) : LREAL
   :noindex:

   Get 4-quadrant arc-tangent in degrees.

You can also use directive parameters to describe your object:

.. code-block:: rst

   .. function:: Atan2()

      :var_in LREAL y: Vertical distance
      :var_in LREAL x: Horizontal distance
      :rtype: LREAL

      Get 4-quadrant arc-tangent in degrees.

.. function:: Atan2()
   :noindex:

   :var_in LREAL y: Vertical distance
   :var_in LREAL x: Horizontal distance
   :rtype: LREAL

   Get 4-quadrant arc-tangent in degrees.
