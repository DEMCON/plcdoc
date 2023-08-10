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

**Examples:**

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


functionblock
=============

.. code-block:: rst

   .. functionblock:: <signature>
      <...>

The same options from `function <#function>`_ are available.

**Examples:**

.. code-block:: rst

   .. functionblock:: MyFunctionBlock

      :var_input LREAL myInput:
      :var_output LREAL myOutput:

.. functionblock:: MyFunctionBlock
   :noindex:

   :var_input LREAL myInput:
   :var_output LREAL myOutput:

You can also nest e.g. methods and properties:

.. code-block:: rst

   .. functionblock:: MyFunctionBlock
      :noindex:

      .. method:: MyMethod(input: BOOL) : STRING

      .. property:: Parameter : LREAL

.. functionblock:: MyFunctionBlock
   :noindex:

   .. method:: MyMethod(input: BOOL) : STRING
      :noindex:

   .. property:: Parameter : LREAL
      :noindex:


method
======

.. code-block:: rst

   .. method:: <signature>
      <...>

The same options from `function <#function>`_ are available.


property
========

.. code-block:: rst

   .. property:: <signature>

**Examples:**

.. code:: rst

   .. property:: someProp : BOOL

.. property:: someProp : BOOL
   :noindex:


enum / enumerator
=================

.. code-block:: rst

   .. enum:: <name>

      .. enumerator:: <values>

**Examples:**

It is common to immediately next the possible values:

.. code-block:: rst

   .. enum:: Color

      .. enumerator:: \
         BLUE
         RED
         GREEN

.. enum:: Color
   :noindex:

   .. enumerator:: \
      BLUE
      RED
      GREEN


struct
======

.. code-block:: rst

   .. struct:: <name>

      .. member:: <name>

**Examples:**

.. code-block:: rst

   .. struct:: Time

      .. member:: Hour
      .. member:: Minute
      .. member:: Second

.. struct:: Time
   :noindex:

   .. member:: Hour
      :noindex:
   .. member:: Minute
      :noindex:
   .. member:: Second
      :noindex:
