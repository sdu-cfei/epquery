.. EPQuery documentation master file, created by
   sphinx-quickstart on Sun Jul 23 11:08:40 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============
Introduction
============

**EPQuery** is a Python package for exploring and editing `EnergyPlus`_ models. 
The tool helps to automate many tedious tasks, especially
when it comes to large models with thousands of objects.
With **EPQuery** you can write scripts for adding new schedules, reading the details about the building geometry,
adding external interface objects or applying any other custom modification.

Currently the tool contains mostly generic methods for editing IDF files, e.g. for creating and deleting objects,
reading and modifying fields. Although these methods allow to apply any desired modifications in the model,
their main purpose is to serve as the basis for specialized methods, e.g. for editing building geometry or
adding new schedules. Since the tool is in the early stage of development, the list of specialized methods
is yet limited and the users are welcome to add their own methods. See :ref:`how-to-contribute`.

**EPQuery** is licensed under the permissive BSD 2-clause license. Read the :ref:`License`.

.. _EnergyPlus: https://energyplus.net/

**Contents:**

.. toctree::
   :maxdepth: 3

   installation
   api
   examples
   how-to-contribute
   contributors
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
