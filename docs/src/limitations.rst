######################
Limitations and Issues
######################

For an up-to-date insight on issues, see https://github.com/DEMCON/plcdoc .
Please help maintaining this project by adding any new issues there.

Grammar
=======

Grammar refers to the parsing of PLC code.
This is done through a language specification, custom made in TextX.
And so there is no guarantee that all possible PLC code can be parsed without error.
Nonetheless, much of the most occurring code will parse with no problems.

Expressions
-----------

With expressions we mean all the literally typed constructions, from a simple ``5`` or ``'Hello World!'`` to a more complex ``CONCAT(INT_TO_STRING(5 + 3 * 8), '...')``.

Currently, expressions are not parsed recursively as they would be for a real interpreter.
Instead, when an expression is expected the whole item is simply matched as a string.
So in the following...

.. code-block::

   my_int      : INT := 1 + 1;
   my_string   : STRING := CONCAT("+", MY_CONST);

...the initial values are registered as just ``"1 + 1"`` and ``"CONCAT("+", MY_CONST)"``.
This means e.g. variables are never recognized in variable initialization and won't be linked.
Aside from this, the expression should be printed normally in your generated docs item.

String Escape
-------------

Because `expressions <#Expressions>`_ are typically matched until the next ``;``, this breaks when a literal semicolon appears in a string.
This is avoided specifically for singular string expressions, but not for any expression:

.. code-block::

   str1  : STRING := 'Hi;';               // This will parse
   str2  : STRING := CONCAT('Hi', ';');   // This will cause a parsing error

Workaround
^^^^^^^^^^

For now you might have to use ``$3B`` as a `string constant <https://infosys.beckhoff.com/english.php?content=../content/1033/tc3_plc_intro/2529327243.html&id=>`_ as a replacement for the literal semicolon.
Or introduce (const) variables to break up those expressions.
