from epquery import BasicEdit
from epquery import utilities


class ExtInterface(BasicEdit):

    def add_external_interface(self):
        """
        Adds external interface object *IN PLACE*.
        The object is added at the end of the current IDF.
        Returns the copy of this object.

        :returns: A copy of external interface object
        :rtype: list(str)
        """
        ext_interface = list([
            "ExternalInterface",
            "FunctionalMockupUnitExport"
        ])
        self.add_object(ext_interface)
        
        return ext_interface

    def schedule_to_interface(self, mask, init_val=0, inplace=True):
        """
        Returns external interface objects for schedules.
        Adds the objects to the IDF if *inplace* is *True*.

        .. warning::

            The method does not check if the objects selected in the
            mask are valid schedules. It's the user responsibility.

        :param mask: Mask with selected schedules
        :type mask: list(bool)
        :param float init_val: Initial value of the schedule
        :param bool inplace: If True, original schedules are commented and new are added in place
        :returns: Schedules interface objects
        :rtype: list(list(str))
        """
        intf = list()

        schedules = self.filter(mask)

        for obj in schedules:
            name = self.get_field(obj, 'Name')
            t = list()
            t.append("ExternalInterface:FunctionalMockupUnitExport:To:Schedule")
            t.append("{}".format(name))
            t.append("{}".format(self.get_field(obj, 'Schedule Type Limits Name')))
            t.append("{}".format(name.replace(' ', '_')))
            t.append("{}".format(init_val))  # Initial value
            intf.append(t)

        if inplace:
            self.comment(mask)
            self.add_objects(intf)

        return intf

    def output_to_interface(self, mask, key_values, fmu_names=None, inplace=True):
        """
        Returns external interface objects for Output:Variable.

        .. warning::

            The argument *key_values* is used to expand the interface to all needed objects.
            The method does not read the key value from the Output:Variable object definition.

        .. warning::

            The method is not adapted for use with multiple Output:Variable objects.
            It is possible, however, to add multiple key values within one Output:Variable.

        :param mask: Mask with selected outputs
        :type mask: list(bool)
        :param key_values: Key values from Output:Variable ('*' can't be used)
        :type key_values: list(str)
        :param fmu_names: Custom FMU variable names
        :type fmu_names: None or list(str)
        :param bool inplace: If True, original schedules are commented and new are added in place
        :returns: Schedules interface objects
        :rtype: list(list(str))
        """
        # TODO: Add support for Output:Variable with explicitly defined key name (not '*')
        # TODO: Currently it's not adapted for use with multiple Output:Variable objects

        intf = list()

        outvars = self.filter(mask)

        if fmu_names is None:
            fmu_names = [None for x in range(len(key_values))]

        for obj in outvars:
            for kv, fvn in zip(key_values, fmu_names):
                vn = self.get_field(obj, 'Variable Name')
                if fvn is None:
                    fmu_var_name = vn.replace(' ', '_') + '_' + kv.replace(' ', '_')
                else:
                    fmu_var_name = fvn
                t = list()
                t.append("ExternalInterface:FunctionalMockupUnitExport:From:Variable")
                t.append("{}".format(kv))         # Output:Variable Index Key Name
                t.append("{}".format(vn))     # Output:Variable Name
                t.append("{}".format(fmu_var_name)) # FMU Variable Name
                intf.append(t)

        if inplace:
            self.add_objects(intf)

        return intf