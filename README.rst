=====================================
EPQuery - EnergyPlus IDF editing tool
=====================================

Description
===========

EPQuery is a tool for exploring and editing large IDF files. The tool helps to automate tedious
tasks, like adding new schedules or external interface objects. EPQuery supplies basic methods
for querying the model, selecting different objects and perform basic editing, but the user
can pass custom functions to be used on the selected objects. 

Installation
============

Curently the only way to install the tool is by cloning this repository and installing using pip
from the project directory:

::

    git clone https://github.com/sdu-cfei/epquery.git epquery
    cd epquery
    pip install . 

Author
======

`Krzysztof Arendt <https://github.com/krzysztofarendt>`__, Center for
Energy Informatics, University of Southern Denmark

License
=======

Copyright (c) 2017, University of Southern Denmark. All rights reserved.

This code is licensed under BSD 2-clause license. See
`LICENSE </LICENSE>`__ file in the project root for license terms.
