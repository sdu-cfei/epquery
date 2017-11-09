.. _Examples:

Examples
========

**Initialization:**

.. code::

    >>> import epquery
    >>> idf = 'my_model.idf'
    >>> idd = 'Energy+.idd'
    >>> ed = epquery.Editor(idf, idd)

**Get zones located in the basement:**

.. code::

    >>> zones = ed.query('Zone', method='words', Name='Basement')  # Select all zones having word 'Basement' in the name
    >>> for z in zones:
    ...     print(z)
    ['Zone', 'Thermal Zone 123 - Basement', '-0', '0', '0', '0', '', '', '', '', '', '', '']
    ['Zone', 'Thermal Zone 124 - Basement', '-0', '0', '0', '0', '', '', '', '', '', '', '']
    ['Zone', 'Thermal Zone 126 - Basement', '-0', '0', '0', '0', '', '', '', '', '', '', '']

**Get surface names of all surfaces of zone Thermal Zone 123 - Basement:**

.. code::

    >>> mask = ed.mask('BuildingSurface:Detailed', method='exact', Zone_Name='Thermal Zone 123 - Basement')  # Select surfaces of the zone 'Thermal Zone 123 - Basement'
    >>> surf_names = ed.get_field(mask, 'Name')  # Get names of the selected surfaces
    >>> print(surf_names)
    ['aim28692 Reversed', 'aim28794', 'aim28805', 'aim28817', 'aim28839', 'aim28851', 'aim28863', 'aim28875', 'aim28887', 'aim28899', 'aim28911']

**Get surface vertices of above selected surfaces:**

.. code::

    >>> vertices = list()
    >>> for s in surf_names:
    ...     vertices.append(ed.get_surface_vertices(s))  # Get vertices of the surface named *s*
    >>> for s, v in zip(surf_names, vertices):
    ...     print('{}: {}').format(s, v)
    aim28692 Reversed: [(5.336593, 49.91195, 21.21), (5.336593, 49.91195, 17.24), (5.30291, 50.36069, 17.24), (5.30291, 50.36069, 21.21)]
    aim28794: [(5.216085, 51.51743, 17.24), (5.336593, 49.91195, 17.24), (3.546628, 49.7776, 17.24), (3.42612, 51.38308, 17.24)]
    aim28805: [(3.42612, 51.38308, 21.21), (3.42612, 51.38308, 17.24), (3.546628, 49.7776, 17.24), (3.546628, 49.7776, 21.21)]
    aim28817: [(3.546628, 49.7776, 21.21), (3.546628, 49.7776, 17.24), (5.336593, 49.91195, 17.24), (5.336593, 49.91195, 21.21)]
    aim28839: [(5.30291, 50.36069, 21.21), (5.30291, 50.36069, 17.24), (5.216085, 51.51743, 17.24), (5.216085, 51.51743, 21.21)]
    aim28851: [(3.819042, 49.85575, 21.21), (3.823349, 49.79837, 21.21), (3.546628, 49.7776, 21.21), (3.542321, 49.83498, 21.21)]
    aim28863: [(5.216085, 51.51743, 21.21), (5.288876, 50.54766, 21.21), (5.281397, 50.5471, 21.21), (5.208606, 51.51687, 21.21)]
    aim28875: [(5.288876, 50.54766, 21.21), (5.336593, 49.91195, 21.21), (5.329113, 49.91139, 21.21), (5.281397, 50.5471, 21.21)]
    aim28887: [(5.324807, 49.96877, 21.21), (5.329113, 49.91139, 21.21), (3.823349, 49.79837, 21.21), (3.819042, 49.85575, 21.21)]
    aim28899: [(3.542321, 49.83498, 21.21), (5.324807, 49.96877, 21.21), (5.208606, 51.51687, 21.21), (3.42612, 51.38308, 21.21)]
    aim28911: [(5.216085, 51.51743, 21.21), (5.216085, 51.51743, 17.24), (3.42612, 51.38308, 17.24), (3.42612, 51.38308, 21.21)]

**Add external interface and save new IDF:**

.. code::

    >>> ed.add_external_interface()                     # Add external interface header to IDF
    >>> zones = ed.mask('Zone')                         # Select all zones
    >>> zone_names = ed.get_field(zones, 'Name')        # Get zone names
    >>> air_temp = ed.mask('Output:Variable', Variable_Name='Zone Air Temperature')  # Select zone air temperature output
    >>> ed.output_to_interface(air_temp, zone_names)    # Add external interface outputs for all zones
    >>> ed.to_idf('my_new_model.idf')                   # Save modified IDF

**Manually create some object and add it to IDF:**

.. code::

    >> ed.create_object('ExternalInterface:FunctionalMockupUnitExport:From:Variable', OutputVariable_Index_Key_Name='Zone 1', OutputVariable_Name='Zone Air Temperature', FMU_Variable_Name='Zone 1 Temperature')

.. note::

    There is no need to create ``ExternalInterface:FunctionalMockupUnitExport:From:Variable`` manually, because there exists a specialized method for this (See :ref:`ExtInterface`).
    However this example shows how to create objects which contain special characters in field names. **EPQuery** can deal with inaccurate field names and tries
    to match your description to the object template from the IDD file. Therefore, the best strategy is to simply omit any special characters in the field names.
    In addition, it is advised to replace all spaces with underscores.

**Print info about object:**

.. code::

    >>> info = ed.get_object_info('ZoneHVAC:AirDistributionUnit')
    >>> print(info)
    ZoneHVAC:AirDistributionUnit
        \memo Central air system air distribution unit
        \serves as a wrapper for a specific type of
        \memo air terminal unit. This object is referenced in a ZoneHVAC:EquipmentList.
        \min-fields 4
    A1    \field Name
        \required-field
        \reference ZoneEquipmentNames
    A2    \field Air Distribution Unit Outlet Node Name
        \required-field
        \type node
    A3    \field Air Terminal Object Type
        \type choice
        \key AirTerminal:DualDuct:ConstantVolume
        \key AirTerminal:DualDuct:VAV
        \key AirTerminal:SingleDuct:ConstantVolume:Reheat
        \key AirTerminal:SingleDuct:ConstantVolume:FourPipeBeam
        \key AirTerminal:SingleDuct:VAV:Reheat
        \key AirTerminal:SingleDuct:VAV:NoReheat
        \key AirTerminal:SingleDuct:SeriesPIU:Reheat
        \key AirTerminal:SingleDuct:ParallelPIU:Reheat
        \key AirTerminal:SingleDuct:ConstantVolume:FourPipeInduction
        \key AirTerminal:SingleDuct:VAV:Reheat:VariableSpeedFan
        \key AirTerminal:SingleDuct:VAV:HeatAndCool:Reheat
        \key AirTerminal:SingleDuct:VAV:HeatAndCool:NoReheat
        \key AirTerminal:SingleDuct:ConstantVolume:CooledBeam
        \key AirTerminal:DualDuct:VAV:OutdoorAir
        \key AirTerminal:SingleDuct:UserDefined
        \key AirTerminal:SingleDuct:Mixer
        \required-field
    A4    \field Air Terminal Name
        \required-field
        \type object-list
        \object-list AirTerminalUnitNames
    N1    \field Nominal Upstream Leakage Fraction
        \note fraction at system design Flow; leakage Flow constant
        \leakage fraction
        \note varies with variable system Flow Rate.
        \type real
        \minimum 0
        \maximum 0.3
        \default 0
    N2    \field Constant Downstream Leakage Fraction
        \type real
        \minimum 0
        \maximum 0.3
        \default 0
