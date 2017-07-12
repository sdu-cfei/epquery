import logging
logger = logging.getLogger(__name__)
import numpy as np
from epquery import BasicEdit
from epquery.geomedit import GeomEdit
from epquery import utilities

# BasicEdit is not needed as the parent class
# because other specialized classes inherit from it
class Editor(GeomEdit):
    """
    High-level API for editing IDF files.
    """

    pass
