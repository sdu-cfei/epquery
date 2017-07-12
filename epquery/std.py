"""
Copyright (c) 2017, University of Southern Denmark
All rights reserved.

This code is licensed under BSD 2-clause license.
See LICENSE file in the project root for license terms.
"""

import numpy as np
from collections import OrderedDict
import math

# Standard functions for Manager.apply()
# =============================================================

def interface_schedule(objects, manager, init_val=0):
    """
    Returns external interface objects for schedules.

    :param objects: Objects to be moved to the interface
    :type objects: list(list(str))
    :param Manager manager: Manager instance
    :param float init_val: Initial value of the schedule
    :rtype: list(list(str))

    Template::

        ExternalInterface:FunctionalMockupUnitExport:To:Schedule,
        , != Name
        , != Schedule Type Limits Name
        , != FMU Variable Name
        ; != Initial Value
    """
    intf = list()

    for obj in objects:
        name = manager.get_field(obj, 'Name')
        t = list()
        t.append("ExternalInterface:FunctionalMockupUnitExport:To:Schedule")
        t.append("{}".format(name))
        t.append("{}".format(manager.get_field(obj, 'Schedule Type Limits Name')))
        t.append("{}".format(name.replace(' ', '_')))
        t.append("{}".format(init_val))  # Initial value
        intf.append(t)

    return intf


def interface_variable(objects, key_values, manager):
    """
    Returns external interface objects for Output:Variable.

    Since usually Output:Variable is defined in IDF with
    *key value* equal \*, *var_names* are used to expand
    the interface to all needed objects.

    :param objects: Objects to be moved to the interface
    :type objects: list(list(str))
    :param key_values: Key values from Output:Variable after expanding \*
    :type key_values: list(str)
    :param Manager manager: Manager instance
    :rtype: list(list(str))

    Template::

        ExternalInterface:FunctionalMockupUnitExport:From:Variable,
        , != Output:Variable Index Key Name
        , != Output:Variable Name
        ; != FMU Variable Name
    """
    intf = list()
    

    for obj in objects:
        for name in key_values:
            var_name = manager.get_field(obj, 'Variable Name')
            fmu_var_name = var_name.replace(' ', '_') + '_' + name.replace(' ', '_')
            t = list()
            t.append("ExternalInterface:FunctionalMockupUnitExport:From:Variable")
            t.append("{}".format(name))
            t.append("{}".format(var_name))
            t.append("{}".format(fmu_var_name))
            intf.append(t)

    return intf


def daylighting_ref_pts(objects, editor):
    """
    Returns Daylighting:ReferencePoint objects for each zone.
    Reference points are put above the floor centroid at z = 0.8 [m].
    **Takes floor surfaces as objects.**

    .. warning::

        If a zone's floor is a patchwork of multiple surfaces,
        boundary vertices are found. However, the result
        on non-rectangular non-symmetric floors is unpredictable.

    :param objects: Floor surfaces (BuildingSurface:Detailed)
    :type objects: list(list(str))
    :param Editor editor: *Editor* instance
    """
    #z = 0.8

    vertices = [editor.get_surface_vertices(editor.get_field(x, 'Name')) for x in objects]
    zone_names = [editor.get_field(x, 'Zone Name') for x in objects]

    # Get min max xyz
    minmax = dict()
    for zone, points in zip(zone_names, vertices):
        if zone not in minmax:
            minmax[zone] = {
                'xmin': points[0][0], 'xmax': points[0][0],
                'ymin': points[0][1], 'ymax': points[0][1],
                'zmin': points[0][2], 'zmax': points[0][2],
                }
            
        for v in points:
            if v[0] < minmax[zone]['xmin']:
                minmax[zone]['xmin'] = v[0]
            elif v[0] > minmax[zone]['xmax']:
                minmax[zone]['xmax'] = v[0]
            if v[1] < minmax[zone]['ymin']:
                minmax[zone]['ymin'] = v[1]
            elif v[1] > minmax[zone]['ymax']:
                minmax[zone]['ymax'] = v[1]
            if v[2] < minmax[zone]['zmin']:
                minmax[zone]['zmin'] = v[2]
            elif v[2] > minmax[zone]['zmax']:
                minmax[zone]['zmax'] = v[2]

    # Ref point position
    ref_pos = dict()
    for z in minmax:
        ref_pos[z] = (
            minmax[z]['xmin'] + (minmax[z]['xmax'] - minmax[z]['xmin']) / 2,
            minmax[z]['ymin'] + (minmax[z]['ymax'] - minmax[z]['ymin']) / 2,
            minmax[z]['zmin'] + 0.8
        )

    ref_pts = list()
    count = 0
    for zone in zone_names:
        ref_pts.append(list())
        ref_pts[-1].append('Daylighting:ReferencePoint')
        ref_pts[-1].append('{} RefPoint'.format(zone))       # Name
        ref_pts[-1].append('{}'.format(zone))                # Zone Name
        ref_pts[-1].append('{}'.format(ref_pos[zone][0]))    # X-Coordinate
        ref_pts[-1].append('{}'.format(ref_pos[zone][1]))    # Y-Coordinate
        ref_pts[-1].append('{}'.format(ref_pos[zone][2]))    # Z-Coordinate

        count += 1

    return ref_pts


def schedule_file(objects, editor):
    """
    Returns Schedule:File objects for all *objects*.
    Compatible object types:
    Lights, People, ElectricEquipment, ZoneInfiltration:DesignFlowRate

    :param objects: Compatible objects (see above)
    :param Editor editor: Editor instance
    :rtype: list(list(str))
    """
    sch = list()

    for obj in objects:
        obj_type = obj[0]
        sch_field_name = 'Number of People Schedule Name' if obj_type == 'People' else 'Schedule Name'
        sch_name = editor.get_field(obj, sch_field_name)
        
        sch.append(list())
        sch[-1].append("Schedule:File")
        sch[-1].append(sch_name)
        sch[-1].append('ActivityLevel')
        sch[-1].append('mock_schedule.csv')
        sch[-1].append('2')
        sch[-1].append('0')
        sch[-1].append('8760')
        sch[-1].append('Comma')
        sch[-1].append('No')
    
    return sch


def lights(objects, editor):
    """
    Returns lights definitions for all zones in *objects*.

    .. note::

        Fields in this template need to be modified manually.

    :param objects: Zone objects
    :param Editor editor: Editor instance
    :rtype: list(list(str))
    """
    lights = list()

    zone_names = [editor.get_field(x, 'Name') for x in objects]

    for zone in zone_names:
        lights.append(list())
        lights[-1].append("Lights")  # Object type
        lights[-1].append("Lights {}".format(zone))  # Object name
        lights[-1].append(zone) # Zone
        lights[-1].append("Lights Schedule {}".format(zone)) # Schedule name
        lights[-1].append("Watts/Area") # Design Level Calculation Method
        lights[-1].append("") # Lighting Level {W}
        lights[-1].append("2.9") # Watts per Zone Floor Area {W/m2}
        lights[-1].append("") # Watts per Person {W/person}
        lights[-1].append("") # Return Air Fraction
        lights[-1].append("") # Fraction Radiant
        lights[-1].append("") # Fraction Visible
        lights[-1].append("") # Fraction Replaceable

    return lights


def people(objects, editor):
    """
    Returns people definitions for all zones in *objects*.

    .. note::

        Fields in this template need to be modified manually.

    :param objects: Zone objects
    :param Editor editor: Editor instance
    :rtype: list(list(str))
    """
    people = list()

    zone_names = [editor.get_field(x, 'Name') for x in objects]

    for zone in zone_names:
        people.append(list())
        people[-1].append("People")
        people[-1].append("People {}".format(zone)) # Name
        people[-1].append(zone) # Zone
        people[-1].append("People Schedule {}".format(zone)) # Number of People Schedule Name
        people[-1].append("People") # Number of People Calculation Method
        people[-1].append("1") # Number of People
        people[-1].append("") # People per Zone Floor Area {person/m2}
        people[-1].append("") # Zone Floor Area per Person {m2/person}
        people[-1].append("0.3") # Fraction Radiant
        people[-1].append("") # Sensible Heat Fraction
        people[-1].append("Medium Office Activity") # Activity Level Schedule Name

    return people


def electric_equipment(objects, editor):
    """
    Returns electric equipment definitions for all zones in *objects*.

    .. note::

        Fields in this template need to be modified manually.

    :param objects: Zone objects
    :param Editor editor: Editor instance
    :rtype: list(list(str))
    """
    equip = list()

    zone_names = [editor.get_field(x, 'Name') for x in objects]

    for zone in zone_names:
        equip.append(list())
        equip[-1].append("ElectricEquipment")
        equip[-1].append("El Equip {}".format(zone)) # Name
        equip[-1].append(zone) # Zone
        equip[-1].append("El Equip Schedule {}".format(zone)) # Schedule Name
        equip[-1].append("Watts/Area") # Design Level Calculation Method
        equip[-1].append("") # Design Level {W}
        equip[-1].append("4") # Watts per Zone Floor Area {W/m2}
        equip[-1].append("") # Watts per Person {W/person}
        equip[-1].append("") # Fraction Latent
        equip[-1].append("") # Fraction Radiant
        equip[-1].append("") # Fraction Lost

    return equip


def zone_infiltration(objects, editor):
    """
    Returns zone infiltration design flowrate definitions for
    all zones in *objects*.

    .. note::

        Fields in this template need to be modified manually.

    :param objects: Zone objects
    :param Editor editor: Editor instance
    :rtype: list(list(str))
    """
    inf = list()

    zone_names = [editor.get_field(x, 'Name') for x in objects]

    for zone in zone_names:
        inf.append(list())
        inf[-1].append("ZoneInfiltration:DesignFlowRate")
        inf[-1].append("Infiltration {}".format(zone)) # Name
        inf[-1].append(zone) # Zone
        inf[-1].append("Infiltration Schedule {}".format(zone)) # Schedule Name
        inf[-1].append("Flow/ExteriorArea") # Design Flow Rate Calculation Method
        inf[-1].append("") # Design Flow Rate
        inf[-1].append("") # Flow per Zone Floor Area {m3/s-m2}
        inf[-1].append("0.0008") # Flow per Exterior Surface Area {m3/s-m2}
        inf[-1].append("") # Air Changes per Hour {1/hr}
        inf[-1].append("") # Constant Term Coefficient
        inf[-1].append("") # Temperature Term Coefficient
        inf[-1].append("") # Velocity Term Coefficient
        inf[-1].append("") # Velocity Squared Term Coefficient

    return inf


def daylighting_controls(objects, editor):
    ctrl = list()

    zone_names = [editor.get_field(x, 'Name') for x in objects]

    for zone in zone_names:
        ctrl.append(list())
        ctrl[-1].append('Daylighting:Controls')
        ctrl[-1].append('Daylighting {}'.format(zone))  # Name
        ctrl[-1].append(zone)                           # Zone Name
        ctrl[-1].append('SplitFlux')                    # Daylighting Method
        ctrl[-1].append('')                             # Availability Schedule Name
        ctrl[-1].append('Continuous')                   # Lighting Control Type
        ctrl[-1].append('0')                            # Minimum Input Power Fraction
        ctrl[-1].append('0')                            # Minimum Light Output Fraction
        ctrl[-1].append('')                             # Number of Stepped Control Steps
        ctrl[-1].append('1')                            # Probability Lighting will be reset whe needed in manual stepped control
        ctrl[-1].append('{} RefPoint'.format(zone))     # Glare Calculation Daylighting Reference Point Name
        ctrl[-1].append('90') # Glare calculation azimuth angle of view direction
        ctrl[-1].append('20') # Maximum allowable discomfort glare index
        ctrl[-1].append('') # DElight Gridding Resolution
        ctrl[-1].append('{} RefPoint'.format(zone)) # Reference point name
        ctrl[-1].append('1') # Fraction of zone controlled by reference point
        ctrl[-1].append('500') # Illuminance setpoint

    return ctrl


# Other template functions
# =============================================================

def external_interface_header():
    """
    Returns object representing external interface header.

    :rtype: list(str)
    """
    ext_interface = list([
        "ExternalInterface",
        "FunctionalMockupUnitExport"
    ])
    return ext_interface