"""
Copyright (c) 2017, University of Southern Denmark
All rights reserved.

This code is licensed under BSD 2-clause license.
See LICENSE file in the project root for license terms.
"""

import logging
import copy
import tempfile
import shutil
import os
import collections
from fuzzywuzzy import fuzz
from epquery import log_init
from epquery import idd
from epquery import idf
from epquery import utilities


class BasicEdit(object):
    """
    BasicEdit is used to query and manipulate EnergyPlus model stored
    in IDF file. It contains only basic manipulation methods in its
    API (object type-agnostic). Look into the *Editor* class for more
    specialized methods.

    Use config_logger=True if you want to use default settings for logging.
    Otherwise you have to specify your own logging configuration using the
    logging module.

    :param str idf_path: Path to IDF file
    :param str idd_path: Path to IDD file
    :param bool config_logger: Configure logger using logging.basicConfig
    """

    def __init__(self, idf_path, idd_path, config_logger=False):

        # Default logging configuration?
        if config_logger:
            log_init.config_logger()

        self.logger = logging.getLogger(__name__)

        # Change paths to absolute (relative paths doesn't work with EnergyPlusToFMU)
        idf_path = os.path.abspath(idf_path)
        idd_path = os.path.abspath(idd_path)

        # Instantiate IDF and IDD
        self.idf = idf.IDF(idf_path)
        self.idd = idd.IDD(idd_path)

    def get_object_info(self, obj_type):
        """
        Returns object information based on the IDD file.

        :param str obj_type: Object type, e.g. 'Zone'
        :rtype: str
        """
        return self.idd.get_object_info(obj_type)

    def create_object(self, obj_type, inplace=False, **kwargs):
        """
        Creates and returns a new object of type *obj_type* with fields
        defined by *kwargs*. Fields not provided in *kwargs* are assumed
        to have no value. Spaces in the field names have to be replaced with
        underscores. Field names with special characters have to be provided
        without them, trying to match the name as close as possible, e.g.
        instead of 'Output:Variable Index Key Name'
        write 'OutputVariable_Index_Key_Name' (no semicolon, spaces to underscores).

        .. warning::

            The method may not work with expandable objects
            with unnamed fields.

        :param str obj_type: Object type, e.g. 'Schedule:File'
        :param kwargs: Field names and values
        :param bool inplace: If True, the object is appended to the IDF
        :return: New object
        :rtype: list(str)
        """
        self.logger.info('Creating new object: {}'.format(obj_type))

        field_names = self.idd.get_field_names(obj_type)
        field_names = [f.upper() for f in field_names]

        # Replace underscores in kwargs with spaces
        kwargs = {key.replace('_', ' '): kwargs[key] for key in kwargs}

        # Convert to upper case
        kwargs = {key.upper(): kwargs[key] for key in kwargs}

        # Field names in kwargs may be slightly different than in IDD,
        # because special characters cannot be used in argument names,
        # therefore a mapping is needed
        self.logger.debug('Mapping fields from kwargs with IDD...')
        values = dict()
        for f in field_names:
            self.logger.debug('Processing field: {}'.format(f))
            if f in kwargs:
                self.logger.debug("Field '{}' found in kwargs".format(f))
                values[f] = kwargs[f]
            else:
                # Find closest match
                self.logger.debug("Field '{}' not found in kwargs, looking for closest match...".format(f))
                best = None
                score = 0
                for k in kwargs:
                    ratio = fuzz.ratio(f, k)
                    self.logger.debug("Comparing with '{}', score={}".format(k, ratio))
                    if ratio > score:
                        best = k
                        score = ratio
                # Assign only if found reasonably good match
                if (best is not None) and (score > 50):
                    self.logger.debug("Found reasonable match between '{}' and '{}'".format(f, best))
                    values[f] = kwargs[best]
                else:
                    # Empty value if not a good match
                    self.logger.debug("Did not find reasonable match, assigning empty string")
                    values[f] = ''

        # Make object
        obj = list()
        obj.append(obj_type)

        for f in field_names:
            obj.append(values[f])

        if inplace:
            self.add_object(obj)

        return obj

    def match_fields(self, obj_type, fields):
        """
        Tries to match field names in `fields` with actual field names in IDD.
        In some cases the user cannot use exact field names as arguments to methods,
        because of special characters. This method returns a dictionary
        mapping user field names to IDD field names (user names: IDD names).
        If a field name couldn't be matched, it's mapped to None.

        .. note::

            All strings are converted to upper case, both in user field names
            and IDD field names.

        :param str obj_type: Object type, e.g. 'Zone'
        :param list(str) fields: List of field names
        :return: dict(str: str)
        """
        fields = [f.upper() for f in fields]
        # fields = [f.replace('_', ' ') for f in fields]
        idd_fields = self.idd.get_field_names(obj_type)
        idd_fields = [f.upper() for f in idd_fields]
        matched = dict()

        self.logger.info('Matching fields with IDD...')
        for f in fields:
            self.logger.info('Processing field: {}'.format(f))
            if f in idd_fields:
                self.logger.info("Field '{}' found in IDD".format(f))
                matched[f] = f
            else:
                # Find closest match
                self.logger.info("Field '{}' not found in IDD, looking for the closest match...".format(f))
                best = None
                score = 0
                for k in idd_fields:
                    ratio = fuzz.ratio(f, k)
                    self.logger.debug("Comparing with '{}', score={}".format(k, ratio))
                    if ratio > score:
                        best = k
                        score = ratio
                # Assign only if found reasonably good match
                if (best is not None) and (score > 50):
                    self.logger.info("Found a reasonable match between '{}' and '{}'".format(f, best))
                    matched[f] = best
                else:
                    # Empty value if not a good match
                    self.logger.error("Did not find any reasonable match, assigning None")
                    matched[f] = None

        return matched

    def query(self, keyword, method='exact', **kwargs):
        """
        Returns objects based on given criteria.
        Supports exact matches (*method*='exact'), substring matches
        (*method*='substring'), word matches (*method*='words').

        All methods convert the letters to uppercase before 
        comparing strings, so 'woRd'=='WorD' is True.

        *kwargs* represents field descriptors from IDD (``\\field``).
        If a descriptor contains space, replace it with underscore.

        .. note::

            Field names with special characters have to be provided
            without them, trying to match the name as close as possible, e.g.
            instead of 'Output:Variable Index Key Name'
            write 'OutputVariable_Index_Key_Name' (no semicolon, spaces to underscores).

        :param str keyword: Unique keyword defining object type, e.g. 'Zone'
        :param str method: Search method ('exact', 'substring' or 'words')
        :param kwargs: Field types and required values
        :rtype: list(list(str))

        Example:
        
        .. code::

            >>> ep = BasicEdit('path_to_IDF', 'path_to_IDD')
            >>> objects = ep.query('Zone', method='words', Name='Zone1', Floor_Area=33.5)
        """
        fields = self.idd.get_field_names(keyword)
        field_map = self.match_fields(keyword, kwargs.keys())

        # Replace kwargs keys with matched IDD keys
        # (new keys are in upper case)
        for old_key in kwargs.copy().keys():
            old_key_up = old_key.upper()
            assert field_map[old_key_up] is not None, 'Field {} could not be matched in IDD'.format(old_key)
            kwargs[field_map[old_key_up]] = kwargs.pop(old_key)

        def get_field_index(key, fields):
            index = 1  # First field after object type name
            for f in fields:
                if f.upper() == key.upper():
                    return index
                else:
                    index += 1
            return None

        def comparable(v1, v2, method):
            if method == 'exact':
                return v1.upper() == v2.upper()
            elif method == 'substring':
                return v1.upper() in v2.upper()
            elif method == 'words' or method == 'word':
                match = True
                for word in v1.split(' '):
                    if word.upper() not in v2.upper():
                        match = False
                return match
            else:
                self.logger.error('Unknown compare method: %s', method)
                None

        # Create pattern object
        # Existing objects will be compared to this one
        # type: list of strings and Nones
        # (None is used in fields not present in kwargs)
        pattern = [keyword]
        for f in fields:
            if f in kwargs:
                pattern.append(kwargs[f])
            else:
                pattern.append(None)

        # First match by keywords
        objects = list()
        for obj in self.idf.get_objects():
            name = obj[0]
            if name == keyword:
                objects.append(obj)

        # Secondly remove objects not matching other criteria
        matched = copy.deepcopy(objects)
        for obj in objects:
            for key in kwargs:
                index = get_field_index(key, fields)  # None if key not in fields
                if index is not None:
                    # if obj[index] != kwargs[key]:
                    if not comparable(kwargs[key], obj[index], method):
                        try:
                            matched.remove(obj)
                        except ValueError:
                            # Element already removed due to other condition not met
                            pass
        
        summary  = 'Query summary:\n'
        summary += '==============\n'
        summary += '{:<20} {}\n'.format('Object type:', keyword)
        for key in kwargs:
            summary += '{:<20} {}\n'.format(key.replace('_', ' ') + ':', kwargs[key])
        summary += '--------------\n'
        summary += 'Method: {}'.format(method)
        summary += '\n'
        summary += 'Matches: {}\n'.format(len(matched))

        print(summary)

        return matched

    def mask(self, keyword, method='exact', inverse=False, **kwargs):
        """
        Same as *query()*, but returns a mask (list of bools).
        The mask represents a list of object matches. It can
        be then applied on IDF objects using *apply_mask()*.

        This method is useful if you need to: 
        
        - select some objects and get their indexes
        - select some objects and print IDF without them (*inverse*=False)

        :param str keyword: Unique keyword defining object type, e.g. 'Zone'
        :param str method: Search method ('exact', 'substring' or 'words')
        :param bool inverse: If True, the mask is inversed
        :param kwargs: Field types and required values
        :rtype: list(bool)
        """
        self.logger.debug('Applying mask with parameters: keyword=%s, method=%s, inverse=%s and **kwargs',
                     keyword, method, inverse)

        matched = self.query(keyword, method, **kwargs)
        objects = self.idf.get_objects()

        self.logger.debug('Number of found matches: %d', len(matched))
        self.logger.debug('Total number of objects in IDF: %d', len(objects))

        def true(inverse):
            if inverse:
                return False
            else:
                return True

        mask = list()
        for obj in objects:
            if obj in matched:
                mask.append(true(inverse))
            else:
                mask.append(not true(inverse))

        self.logger.debug('Number of objects in mask: %d', len(mask))

        # Decide if proceed if mask is empty
        if mask.count(True) == 0:
            msg = 'No objects selected in mask, is the query correct? keyword: {}, kwargs: {}'\
                  .format(keyword, kwargs)
            self.logger.warning(msg)
            print(msg)
            while True:
                self.logger.info('Waiting for user input...')
                answer = raw_input('Do you want to proceed? (y/n): ')
                if answer.upper() == 'Y':
                    break
                elif answer.upper() == 'N':
                    self.logger.info('User decided to exit')
                    raise RuntimeError('User triggered exception')
            self.logger.info('User decided to proceed')

        return mask

    def filter(self, mask, ignore_index=True):
        """
        Returns objects for which mask elements are True.
        Does not change the self-stored IDF.

        Index can be ignored. By doing so the resulting list
        includes only matching objects (those where mask is True).
        Otherwise None is put where mask is False. It can be useful
        if the original object positions are to be preserved.

        :param mask: Mask
        :type mask: list(bool)
        :param bool ignore_index: If False, not matching objects are stored as None
        :return: List of objects
        :rtype: list(list(str))
        """
        objects = list()

        index = 0
        for m in mask:
            if m is True:
                objects.append(self.idf.get_object(index))
            else:
                if ignore_index is False:
                    objects.append(None)
            index += 1
    
        return objects

    def apply(self, func, mask, inplace=True, args=[]):
        """
        Applies function *func* to the passed mask.
        
        If *inplace* is True, modifications are applied *IN PLACE* 
        to objects selected in the mask as True. In addition the modified 
        objects are returned by this function. If *inplace* is False,
        then no in place modifications are performed and the modified
        objects are just returned.

        :param function func: Function to be applied
        :param mask: List of booleans, result of *query_mask*
        :type mask: list(bool)
        :param bool inplace: Flag for in-place modification
        :param args: Any other parameters to be passed to *func*
        :type args: list
        :rtype: list(list(str))
        """
        objects = self.idf.get_objects()  # All objects in IDF
        selected = list()  # Selected objects (to be modified)
        indices = list()  # Indices of selected objects in IDF

        # Sanity checks
        assert len(mask) == len(objects), 'Lengths of mask ({}) and objects ({}) do not match'\
                                          .format(len(mask), len(objects))
        if mask.count(True) == 0:
            self.logger.warning('[apply] Mask is empty!')

        # Get indices of unmasked objects
        for i in range(len(mask)):
            if mask[i] is True:
                indices.append(i)
                selected.append(objects[i])

        # Apply function
        selected = func(selected, *args)

        # Reinsert objects to IDF
        if inplace:
            for i, s in zip(indices, selected):
                self.idf.set_object(i, s)

        return selected

    def comment(self, mask):
        """
        Puts '!=' in the begining of each line of the selected objects.
        Edits *IN PLACE* and returns the commented objects.
        
        .. note::

            Currently, commented objects cannot be uncommented!
            It is because they cannot be located by query(),
            which searches for objects compliant with IDD. Also,
            all comment in IDF files are deleted during parsing.

        :param mask: Objects to be commented out
        :type mask: list(bool)
        :returns: Commented objects
        :rtype: list(list(str))
        """
        objects = self.filter(mask)
        index = [x for x, y in enumerate(mask) if y is True]

        com = list()
        for obj, i in zip(objects, index):
            com_obj = ['!= ' + line for line in obj]
            self.idf.set_object(i, com_obj)
            com.append(com_obj)
        return com

    def remove(self, mask):
        """
        Removes selected objects *IN PLACE*. Returns removed objects.

        :param mask: Selected objects
        :type mask: list(bool)
        :returns: A copy of the deleted objects
        :rtype: list(list(str))
        """
        index = [x for x, y in enumerate(mask) if y is True]
        deleted = list()
        for i in sorted(index, reverse=True):
            deleted.append(self.idf.idf.pop(i))

        return deleted

    def add_object(self, obj, index=None):
        """
        Adds a single EnergyPlus object to the IDF.
        If *index* is None, the object is appended
        to the end of IDF. Otherwise it's inserted
        at *index* (using list.insert()).

        :param obj: EnergyPlus object representation
        :type obj: list(str)
        :rtype: None
        """
        self.idf.add_object(obj, index)
        return None

    def add_objects(self, objects):
        """
        Appends IDF *IN PLACE* with EnergyPlus objects stored
        in *objects*. Unlike in *add_object*, index cannot be
        defined by the user. All objects are simply added to
        the end of IDF.

        :param objects: Objects to be added
        :type objects: list(list(str))
        :rtype: None
        """
        for obj in objects:
            self.add_object(obj)
        return None

    def get_index(self, obj_type, method='exact', flatten=True, **kwargs):
        """
        Returns index of the object. If more than one object is found, returns a list
        of indices. If *flatten* is False, then returns a list even if only
        one object is found (single-element list). Returns None if no object
        matches the criteria.

        :param str obj_type: Object type
        :param str method: Search method used in the query ('exact', 'words', 'substring')
        :param kwargs: Field names and values
        :rtype: int or list(int) or None
        """
        mask = self.mask(obj_type, method, **kwargs)
        index = [x for x, y in enumerate(mask) if y is True]
        
        if len(index) == 0:
            self.logger.warning('No object matched the query. get_index() returns None.')
            return None
        elif len(index) == 1 and flatten is True:
            return index[0]
        else:
            return index

    def set_field(self, mask, **kwargs):
        """
        Sets a new value(s) to the field(s) of the selected objects *IN PLACE*.
        In addition returns the modified objects.

        .. warning::

            Does not work with expandable objects with unnamed fields.

        .. warning::

            Currently field names with special characters (e.g. {}/\\) are not supported.

        :param mask: Selected objects
        :type mask: list(bool)
        :param kwargs: Field names and new values
        :returns: A copy of the modified objects
        :rtype: list(list(str))
        """
        # List of indices
        index = [x for x, y in enumerate(mask) if y is True]

        # Objects
        objects = self.filter(mask)
        assert len(objects) > 0, '[set_field] At least one object required...'

        # Set fields
        new_objects = list()
        
        for obj in objects:

            # Make sure the object is not empty
            assert len(obj) > 0, 'Empty object found'

            # Make sure the keys are matching
            obj_type = obj[0]
            fields = self.idd.get_field_names(obj_type)

            keys_ok = True
            for key in kwargs.keys():
                if key not in fields:
                    keys_ok = False

            if keys_ok is False:
                msg = '[set_field] Selected objects do not contain all keys from kwargs'
                self.logger.error(msg)
                raise KeyError(msg)

            # Copy and modify
            new_objects.append(list())
            new_objects[-1].append(obj_type)

            for v, f in zip(obj[1:], fields):
                if f in kwargs:
                    # New value
                    new_objects[-1].append(kwargs[f])
                else:
                    # Original value
                    new_objects[-1].append(v)

        # Replace original objects
        for i, obj in zip(index, new_objects):
            self.idf.set_object(i, obj)

        return None

    def get_field(self, obj, field, flatten=True):
        """
        Generic function for retrieving field values from
        one or more objects defined by *obj*.

        *obj* can be an index to an object, a list of indexes,
        a mask (list of bools), an actual object (list of str),
        or a list of objects (list of list of str). The returned
        field can be a single value or a list of values,
        depending on how many objects are in *obj* and on *flatten*.
        The parameter *flatten* contols the return type in case
        a single object is passed in *obj*. If it's *False*, the
        return value is a single-element list (with a string). Otherwise
        it's just a string.

        *field* must exist in all objects passed/selected in *obj*.

        :param obj: Object(s)
        :type obj: int or list(int) or list(bool) or list(str) or list(list(str))
        :param str field: Field name
        :rtype: str or list(str)
        """
        # Check type of obj
        if isinstance(obj, int):
            obj_single = self.idf.get_object(obj)
            fields = self._get_field_from_one(obj_single, field)
        elif isinstance(obj, list) and (type(obj[0]) is int):
            obj_list = [self.idf.get_object(x) for x in obj]
            fields = self._get_field_from_all(obj_list, field)
        elif isinstance(obj, list) and (type(obj[0]) is bool):
            obj_list = self.filter(obj)
            fields = self._get_field_from_all(obj_list, field)
        elif isinstance(obj, list) and isinstance(obj[0], str):
            fields = self._get_field_from_one(obj, field)
        elif isinstance(obj, list) and isinstance(obj[0], list):
            fields = self._get_field_from_all(obj, field)

        # Flatten if needed
        if flatten and isinstance(fields, list) and len(fields) == 1:
            fields = fields[0]
        elif not flatten and isinstance(fields, str):
            fields = [fields]

        return fields

    def _get_field_from_one(self, obj, field):
        """
        Returns the value of the requested field.

        :param obj: EnergyPlus object representation
        :type obj: list(str)
        :param str field: Field name (from IDD)
        :returns: Field value or none if field doesn't exist
        :rtype: str or None
        """
        object_name = obj[0]
        field_names = self.idd.get_field_names(object_name)

        index = 1  # Because at index=0 the object type is stored
        for f in field_names:
            if f == field:
                return obj[index]
            else:
                index += 1
        self.logger.warning('Field not found in {}: {}'.format(object_name, field))
        return None

    def _get_field_from_all(self, objects, field):
        """
        Returns a list of values of the requested field from all passed objects.

        :param objects: List of EnergyPlus object representations
        :type objects: list(list(str))
        :param str field: Field name (from IDD)
        :rtype: list(str)
        """
        fields = list()
        for obj in objects:
            fields.append(self.get_field(obj, field))
        return fields

    def to_idf(self, path):
        """
        Prints IDF object to a file.
        
        All fields are described  with comments. 
        Comments start with '!=' to distinguish comments 
        added by EPQuery from standard EnergyPlus comments ('!')
        or OpenStudio comments ('!-').

        :param str path: Path to the output file
        :rtype: None
        """
        self.logger.debug('Attempting to save IDF to file: %s', path)

        idf_obj = self.idf.get_objects()

        # Drop elements with value None
        idf = [x for x in idf_obj if x is not None]

        # Generate string
        idf_str = ""
        min_width = 45
        for obj in idf:
            self.logger.debug('    Printing object: %s (%s)', obj[0], obj[1])

            # Check if object is commented out
            if obj[0].strip()[0] == '!':
                commented = True
            else:
                commented = False
            
            # Get field descriptions if not commented out
            if not commented:
                desc = self.idd.get_field_names(obj[0])
            else:
                desc = ['' for x in range(len(obj))]

            # Remember that *obj* list has one more element than *desc*
            # because object name is not included
            desc.insert(0, None)

            # Extend desc in case there are more fields than descriptions
            # (it happens in extensible objects)
            if len(obj) > len(desc):
                empty = ['' for x in range(len(obj) - len(desc))]
                desc.extend(empty)

            # Add to string
            field_num = 0
            for field, comment in zip(obj, desc):
                first = True if field_num == 0 else False
                last = True if field_num == len(obj) - 1 else False
                width = 45

                if first:
                    line = "{:<}\n".format(field + ',')
                elif (not first) and (not last):
                    line = "    {:<{width}} {}\n".format(field + ',', ' != ' + comment,
                                                         width=max(width, len(field)))
                elif last:
                    line = "    {:<{width}} {}\n".format(field + ';', ' != ' + comment,
                                                         width=max(width, len(field)))
                else:
                    raise Exception('Something went wrong...')
                idf_str += line
                field_num += 1

            idf_str += '\n'

        # Save file
        with open(path, 'w') as f:
            f.write(idf_str)

        return None

    def to_fmu(self, script, epw, name=None, directory=None):
        """
        Saves the model to IDF and exports to an FMU using
        EnergyPlusToFMU tool.

        If *name* and *directory* are not given, the output files are saved
        in the current working directory with the following names:
        ``out.idf``, ``out.fmu``.

        :param str script: Path to EnergyPlusToFMU.py
        :param str epw: Path to EPW weather file
        :param str name: IDF/FMU file name (without extension, avoid dashes), optional
        :param str directory: Output directory if other than CWD, optional
        :returns: Path to the generated FMU
        :rtype: str
        """
        if name is None:
            name = 'out'

        if directory is None:
            directory = os.getcwd()

        # Change paths to absolute
        directory = os.path.abspath(directory)
        script = os.path.abspath(script)
        epw = os.path.abspath(epw)

        self.logger.info('Saving to FMU in {}'.format(directory))

        # Save IDF
        idf = os.path.join(directory, '{}.idf'.format(name))
        self.to_idf(idf)

        # Save FMU
        fmu = utilities.create_fmu(script, self.idd.path, epw, idf, out_dir=directory)

        return fmu
