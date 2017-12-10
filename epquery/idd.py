"""
Copyright (c) 2017, University of Southern Denmark
All rights reserved.

This code is licensed under BSD 2-clause license.
See LICENSE file in the project root for license terms.
"""

import logging
import re
import sys
from collections import OrderedDict


class IDD(object):
    "IDD parser."
    ENCODING = 'cp437'

    def __init__(self, idd_path):
        """
        :param str idd_path: Path to IDD file
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('IDD instance created')
        self.idd = self._parse_idd(idd_path)
        self.path = idd_path

    def get_groups(self):
        """
        :returns (list(str)):
        """
        return self.idd.keys()
    
    def get_group(self, obj):
        """
        Returns group name of the object or None
        if object does not exist.

        :param str obj: Object name
        :rtype: str or None
        """
        for group in self.idd:
            for obj_id in self.idd[group]:
                if obj_id == obj:
                    return group
        return

    def get_objects(self, group=None):
        """
        Returns object names from IDD belonging to
        ``group`` or all if ``group=None``.

        :param group: Group name, returns all objects if None
        :type group: str or None
        :rtype: list(str)
        """
        if group is None:
            objects = list()
            for group in self.idd.keys():
                objects.extend(self.idd[group].keys())
            return objects
        else:
            return self.idd[group].keys()

    def get_object_info(self, obj_type, full=True):
        """
        Returns formatted string with object documentation.

        :param str obj_type: Object type (e.g. 'Schedule:File')
        :param bool full: If True, all field descriptors are included
        :rtype: str        
        """
        obj_dict = self._get_object(obj_type)
        obj_str = ""
        first_field = True

        for k in obj_dict:
            if first_field:
                obj_str += k + '\n'
                first_field = False
            else:
                obj_str += k
            if full:
                for line in obj_dict[k].split('\n'):
                    obj_str += '    ' + line + '\n'
            else:
                first_line = obj_dict[k].split('\n')[0]
                obj_str += '    ' + first_line + '\n'
        return obj_str

    def get_field_ids(self, obj_type):
        """
        Returns field identificators of the object (A1, A2, ..., N1, N2, ...).

        :param str obj_type: Object name
        :rtype: listr(str)
        """
        assert isinstance(obj_type, str), 'Incorrect type of obj_type (should be str)'
        obj_dict = self._get_object(obj_type)
        if obj_dict is not None:
            fields = [x for x in self._get_object(obj_type).keys() if x != obj_type]
        else:
            msg = 'Object does not exist in Energy+.idd: {}'.format(obj_type)
            self.logger.error(msg)
            raise ValueError(msg)
        return fields

    def get_field_names(self, obj_type):
        """
        Returns field names of the object, i.e. '\\field' descriptions
        of fields A1, A2, ..., N1, N2, ...

        :param str obj_type: Object type
        :rtype: list(str) 
        """
        field_ids = self.get_field_ids(obj_type)
        obj_dict = self._get_object(obj_type)
        fields = [obj_dict[x] for x in field_ids]
        merged = ""
        for f in fields:
            merged += f
        # Get only the field name
        fields = re.findall(r'\\field *?.*', merged)
        fields = [x.replace('\\field', '').strip() for x in fields]
        return fields

    def _get_object(self, obj_type):
        """
        Returns object dictionary (field id: field description),
        containing all information from IDD. Returns None if
        object does not exist.

        :param str obj_type: Object type
        :rtype: OrderedDict(str, str) or None
        """
        assert isinstance(obj_type, str), 'Wrong type of obj_type (should be str)'

        for group in self.idd:
            for obj_id in self.idd[group]:
                if obj_id == obj_type:
                    return self.idd[group][obj_id]

        msg = "Invalid object type (does not exist in Energy+.idd): {}".format(obj_type)
        self.logger.error(msg)
        raise ValueError(msg)
        return None

    def _parse_idd(self, idd_path):
        """
        Returns dictionary containing IDD metadata.

        .. warning::

            Minor BUG: If commas are present in field descriptions,
            they are not printed correctly. However it does not affect
            the general functionality of EPQuery. To solve this issue 
            this method has to be revised.

        :param str idd_path: Path to IDD file
        :rtype: OrderedDict(str, OrderedDict(str, OrderedDict(str, str))
        """
        # OrderedDict(str: OrderedDict(str: OrderedDict(str: str)))
        #              ^                ^                ^    ^
        #            group            object           field description
        idd = OrderedDict()

        # Read IDD file
        self.logger.debug('Trying to open file %s', idd_path)

        if sys.version_info[0] >= 3.:
            with open(idd_path, encoding=IDD.ENCODING) as f:
                original_lines = f.readlines()
        else:
            with open(idd_path) as f:
                original_lines = f.readlines()
        
        # Delete comments
        self.logger.debug('Deleting comments from IDD file')
        lines = list()
        for l in original_lines:
            lines.append(l.split('!')[0].strip())
        del original_lines

        # Reconstruct continuous string
        self.logger.debug('Reconstructing continuous string from lines')
        iddstr = ""
        for l in lines:
            iddstr += l + '\n'
        del lines

        # Groups
        self.logger.debug('Getting group names from IDD')
        groups_dict = OrderedDict()  # OrderedDict(str: str)
        groups = re.split(r'\\ *?group', iddstr, flags=re.IGNORECASE)
        groups = [x.strip() for x in groups]
        groups = groups[1:]  # Neglect everything before first group definition
        for g in groups:
            gsplit = g.split('\n')
            group_name = gsplit[0]  # str
            group_str = '\n'.join(gsplit[1:])
            groups_dict[group_name] = group_str  # str
        del iddstr
        del groups

        # Objects and fields
        self.logger.debug('Getting object names, field IDs and descriptions from IDD')
        for group_name in groups_dict.keys():
            self.logger.debug('Processing group: %s', group_name)
            idd[group_name] = OrderedDict()
            all_objects = groups_dict[group_name]  # str
            sep_objects = re.split(r'\n\n+', all_objects.strip(), flags=re.IGNORECASE)  # list(str)
            for obj in sep_objects:
                obj_dict = OrderedDict()
                obj_split = obj.split(',', 1)
                obj_name = obj_split[0].strip()  # str
                self.logger.debug('    Processing object: %s', obj_name)
                fields_str = obj_split[1].strip()  # str

                # Split into descriptions and ids
                desc_and_ids = re.split(r'[\\\n,]', fields_str, flags=re.IGNORECASE)

                # Remove empty elements
                desc_and_ids = [x for x in desc_and_ids if x.strip() != '']

                # Remove commas and semicolons
                for i in range(len(desc_and_ids)):
                    if desc_and_ids[i][0] in ['A', 'N']:
                        desc_and_ids[i] = desc_and_ids[i].replace(',', ' ')
                        desc_and_ids[i] = desc_and_ids[i].replace(';', ' ')
                        desc_and_ids[i] = desc_and_ids[i].strip()

                # Merge multiline descriptions
                ids = list()
                desc = list()
                ids.append(obj_name)
                desc.append('')
                for el in desc_and_ids:
                    if el[0] in ["A", "N"]:
                        ids.append(el)
                        desc.append('')
                    else:
                        desc[-1] += '\\' + el.strip() + '\n'
                
                assert len(ids) == len(desc), 'Parsing error'

                # Fill dict
                for i, d in zip(ids, desc):
                    obj_dict[i] = d

                # Add to idd
                idd[group_name][obj_name] = obj_dict

        return idd
