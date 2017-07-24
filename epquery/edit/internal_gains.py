from epquery import BasicEdit
from epquery import utilities


class InternalGains(BasicEdit):
    "Methods for internal gains definitions."

    def lights(self, mask, inplace=True):
        """
        Returns lights definitions for all zones selected in *mask*.
        Adds these objects to IDF if *inplace* is *True*.
        Object names are constructed as "Lights Zone Name".

        .. warning::

            This method is not ready for end users. The fields in this template
            need to be modified manually at the moment.

        :param mask: Mask with selected zones
        :type mask: list(bool)
        :param bool inplace: Adds objects in place if *True*
        :rtype: list(list(str))
        """
        # TODO: Fields in this methods have to be given by the user and not be static
        # TODO: use BasicEdit.create_object()

        lights = list()

        zone_names = self.get_field(mask, 'Name')

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

    def people(self, mask):
        # TODO: Move from std.py
        pass
    
    def electric_equipment(self, mask):
        # TODO: Move from std.py
        pass