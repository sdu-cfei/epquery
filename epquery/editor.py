import logging
logger = logging.getLogger(__name__)
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
    High-level API for editing IDF files.
    """
    pass
