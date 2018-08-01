"""
Copyright (c) 2017, University of Southern Denmark
All rights reserved.

This code is licensed under BSD 2-clause license.
See LICENSE file in the project root for license terms.
"""

import logging
import time
import os
import shutil
import subprocess

import epquery as epq
import epquery.download as download

# Paths to EnergyPlus exec and weather file
# ==========================================
epexe = "C:\\EnergyPlus\\EnergyPlusV8-8-0\\energyplus.exex"
weather = "C:\\EnergyPlus\\EnergyPlusV8-8-0\\WeatherData\\USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"

for f in [epexe, weather]:
    if not os.path.exists(f):
        msg = \
            "File does not exist: {}\n".format(f) + \
            "Please update paths in this script..."
        raise FileNotFoundError(msg)

# Prepare inputs
# ==============
# Make sure output directory exists and create otherwise
outdir = os.path.join('examples', 'output')
if not os.path.exists(outdir):
    os.makedirs(outdir)

# Download IDF
idf = os.path.join(outdir, '1ZoneUncontrolled.idf')
download.get_test_idf(name='1ZoneUncontrolled', ver='8.8.0', 
    save_path=idf)

# Download IDD
idd = os.path.join(outdir, 'Energy+.idd')
download.get_idd(8, idd)

# Check E+ version and download corresponding IDD
ed = epq.Editor(idf, idd, config_logger=True)

# Do some stuff...
# ================

# Delete this object:
#   Construction,
#     ROOF31,                  !- Name
#     R31LAYER;                !- Outside Layer
mask = ed.mask('Construction', Name='ROOF31')
ed.remove(mask)

# Add the object again using create_object()
ed.create_object('Construction', inplace=True,
    Name="ROOF31",
    Outside_Layer="R31LAYER"
)

ed.to_idf(idf)

# Simulate
# ========
status = subprocess.call([epexe, '-w', weather, '-d', outdir, idf])
print("Simulation status: {}".format(status))
