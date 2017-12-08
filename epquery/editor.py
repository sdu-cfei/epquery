import numpy as np
from epquery.edit import Geometry
from epquery.edit import ExtInterface
from epquery.edit import Schedule

# BasicEdit is not needed as the parent class
# because other specialized classes inherit from it
class Editor(
        Geometry,
        ExtInterface,
        Schedule
    ):
    """
    Public API of EPQuery. This class inherits all methods defined in :ref:`BasicEdit`
    as well as in the :ref:`specialized-classes`.
    
    **Examples:**

    1) Select all zones having words `first` and `floor` in their names and then 
    read get a list with full names of these zones:

    .. code::

        >>> from epquery import Editor
        >>> ed = Editor(path_to_idf, path_to_idd)
        >>> mask = ed.mask('Zone', method='words', Name='first floor')
        >>> names = ed.get_field(mask, 'Name')
        >>> print(names)
        ['Living room first floor', 'Hall first floor', 'Bedroom first floor']
    """
    pass
