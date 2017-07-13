from epquery import BasicEdit
from epquery import utilities


class ExtInterface(BasicEdit):

    def schedule_to_interface(self, mask, init_val=0, inplace=True):
        """
        Returns external interface objects for schedules.
        Does not add the new objects to the IDF.

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