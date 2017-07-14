from epquery import BasicEdit
from epquery import utilities


class Schedule(BasicEdit):

    def definition_to_schedule_file(self, mask, file_name, column_number, inplace=True):
        """
        Creates Schedule:File objects for all objects selected in *mask*.
        Adds the schedules to the IDF if *inplace* is True.
        Returns the created schedule objects.

        Compatible definition objects:
        Lights, People, ElectricEquipment, ZoneInfiltration:DesignFlowRate

        :param mask: Selected definition objects
        :type mask: list(bool)
        :param str file_name: Schedule file name
        :param int column_number: Column number
        :returns: A copy of the schedule objects
        :rtype: list(list(str))
        """
        objects = self.filter(mask)
        sch = list()

        for obj in objects:
            obj_type = obj[0]
            sch_field_name = 'Number of People Schedule Name' if obj_type == 'People' else 'Schedule Name'
            sch_name = self.get_field(obj, sch_field_name)
            
            sch.append(list())
            sch[-1].append("Schedule:File")
            sch[-1].append(sch_name)            # Name
            sch[-1].append('ActivityLevel')     # Schedule Type Limits Name
            sch[-1].append(file_name)           # File Name
            sch[-1].append(str(column_number))  # Column Number
            sch[-1].append('0')                 # Rows to Skip at Top
            sch[-1].append('8760')              # Number of Hours of Data
            sch[-1].append('Comma')             # Column Separator
            sch[-1].append('No')                # Interpolate to Timestep
    
        if inplace:
            self.add_objects(sch)

        return sch