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


class IDF(object):
    """
    This class is used to parse and handle IDF files.
    """
    ENCODING = 'cp437'

    def __init__(self, idf_path=None, idf_obj=None):
        """
        Instantiates IDF object based on the given path
        or list of lists of strings representing IDF
        (list of objects, where each object is a list
        of fields).

        None can be used in the list of objects to indicate
        non-existent objects. Non-existent objects are
        omitted during printing to IDF file.

        :param str idf_path: Path to IDF file
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('IDF instance created')

        if idf_path is not None:
            self.idf = self._parse_idf(idf_path)
        elif idf_obj is not None:
            self.idf = idf_obj
        else:
            msg = 'Cannot instantiate IDF, neither path nor object passed'
            self.logger.error(msg)
            raise ValueError(msg)

    def get_object(self, index):
        """
        Returns object stored at *index*.

        :param int index: Index of idf list
        :return: Object representation
        :rtype: list(str)
        """
        return self.idf[index]

    def set_object(self, index, obj):
        """
        Replaces object at *index* with *obj*.

        :param int index: Index
        :param obj: E+ object representation
        :type obj: list(str)
        :rtype: None
        """
        self.idf[index] = obj
        return None

    def add_object(self, obj, index=None):
        """
        Adds EnergyPlus object to the IDF.
        If *index* is None, the object is appended
        to the end of IDF. Otherwise it's inserted
        at *index* (using list.insert()).

        :param obj: EnergyPlus object representation
        :type obj: list(str)
        :rtype: None
        """
        if index is None:
            self.idf.append(obj)
        else:
            self.idf.insert(index, obj)
        return None

    def get_objects(self):
        """
        Returns parsed objects. All fields are
        represented as strings, even numeric values.

        :returns: List of lists (objects) of strings (fields)
        :rtype: list(list(str))
        """
        return self.idf

    def _parse_idf(self, idf_path):
        """
        Parses IDF and returns list of lists with objects and their fields.

        :param str idf_path: Path to IDF
        :rtype: list(list(str))
        """
        idf = list()

        # Read IDF file
        self.logger.debug('Trying to open file %s', idf_path)
        if sys.version_info[0] >= 3.:
            with open(idf_path, encoding=IDF.ENCODING) as f:
                original_lines = f.readlines()
        else:
            with open(idf_path) as f:
                original_lines = f.readlines()

        # Delete comments
        self.logger.debug('Deleting comments from IDF file')
        lines = list()
        for l in original_lines:
            lines.append(l.split('!')[0].strip())
        del original_lines

        # Reconstruct continuous string
        self.logger.debug('Reconstructing continuous string from lines')
        idfstr = ""
        for l in lines:
            idfstr += l + '\n'
        del lines

        # Get list of object strings
        self.logger.debug('Splitting string into object strings')
        objects = re.split(r';', idfstr)
        objects = [x.strip() for x in objects]

        # Delete any empty objects left after splitting
        self.logger.debug('%d empty string(s) found after splitting. Deleting...', objects.count(''))
        objects = [x for x in objects if x != '']

        # Add objects to idf
        for obj_str in objects:
            fields = obj_str.split(',')
            fields = [x.strip() for x in fields]
            idf.append(fields)
        
        # Sanity checks
        for obj in idf:
            msg = "Empty object found, shouldn't be here"
            assert obj != '', msg
            assert obj is not None, msg
            assert obj[0] != '', msg
            assert obj[0] is not None, msg

        self.logger.debug('Number of found objects: %d', len(idf))
        return idf