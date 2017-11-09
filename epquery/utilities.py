"""
Copyright (c) 2017, University of Southern Denmark
All rights reserved.

This code is licensed under BSD 2-clause license.
See LICENSE file in the project root for license terms.
"""

import os
import shutil
import tempfile
import numpy as np


def create_fmu(script, idd, epw, idf, out_dir):
    """
    Uses EnergyPlusToFMU tool to export model to FMU.
    The FMU is saved in the current working directory with
    the same name as *idf* (but with .fmu extension).

    :param str script: Path to EnergyPlusToFMU.py
    :param str idd: Path to Energy+.idd
    :param str epw: Path to *.epw weather file
    :param str idf: Path to idf file
    :param str out_dir: Output directory path. CWD if None.
    :returns: Path to FMU
    :rtype: str
    """
    # Create temporary directory
    tempdir = tempfile.mkdtemp()

    # Save CWD and switch to temp dir
    cwd = os.getcwd()
    os.chdir(tempdir)
    if out_dir is None:
        out_dir = cwd

    # Get IDF file name
    idf_file = idf.replace('.idf', '')
    idf_file = idf_file.split(os.sep)[-1]

    # Call EnergyPlusToFMU and generate FMU
    os.system('python ' + script + ' -i ' + idd + ' -w ' + epw + ' -d ' + idf)

    # Move FMU to CWD
    temp_fmu_file = os.path.join(tempdir, idf_file + '.fmu')
    out_fmu_path = os.path.join(out_dir, temp_fmu_file.split(os.sep)[-1])
    if os.path.exists(out_fmu_path):
        print('Path already exists: {}'.format(out_fmu_path))
        print('Replacing with new FMU...')
        os.remove(out_fmu_path)
    shutil.move(temp_fmu_file, out_fmu_path)

    # Switch back to CWD
    os.chdir(cwd)

    # Delete temp dir
    shutil.rmtree(tempdir)

    return out_fmu_path


def polygon_area(vertices):
    """
    Returns surface area of a 2D polygon (convex or non-convex).
    Calculation method: Shoelace formula.

    The vertices should be passed as a list of tuples with (x, y)
    coordinates, e.g.::

        vertices = [(0, 0), (0, 2), (2, 0), (2, 2)]

    :param vertices: List of vertices
    :type vertices: list(tuple(float, float))
    :returns: Surface area
    :rtype: float
    """
    zipped = zip(*vertices)
    x = zipped[0]  # X coordinates
    y = zipped[1]  # Y coordinates

    A = 0.5 * np.abs(np.dot(x, np.roll(y,1)) - np.dot(y, np.roll(x,1)))

    return A


if __name__ == "__main__":

    # Example: polygon_area
    p1 = (1, 0)  # Point 1
    p2 = (2, 0)  # Point 2
    p3 = (2, 2)  # Point 3
    p4 = (0, 2)  # Point 4
    p5 = (0, 1)
    p6 = (1, 1)

    A = polygon_area([p1, p2, p3, p4, p5, p6])
    print(A)