.. _API:

=================
API documentation
=================

The end users need to instantiate only the :ref:`Editor` class, which inherits all generic and specialized
methods.

If you would like to add your own methods, you should add it to the one of the existing :ref:`specialized-classes`
or create a new specialized class. All specialized classes inherit from :ref:`BasicEdit`, which provides generic
methods to handle IDF objects.

.. image:: gfx/epquery-classes.png

**Classes:**

.. toctree::
   :maxdepth: 2

   modules/editor
   modules/basicedit
   modules/specialized
   modules/idf
   modules/idd