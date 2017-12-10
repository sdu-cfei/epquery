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
import epquery as epq
import epquery.download as download

# Prepare inputs
# ==============

# Make sure output directory exists and create otherwise
outdir = os.path.join('examples', 'output')
if not os.path.exists(outdir):
    os.makedirs(outdir)

# Configure logging
log_path = os.path.join(outdir, 'epquery.log')
logging.basicConfig(filename=log_path, filemode='w', level='DEBUG',
                    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s')

# Download IDF
idf = os.path.join(outdir, '1ZoneUncontrolled.idf')
download.get_test_idf(name='1ZoneUncontrolled', ver='8.8.0', 
    save_path=idf)

# Download IDD
idd = os.path.join(outdir, 'Energy+.idd')
download.get_idd(8, idd)

# Check E+ version and download corresponding IDD
ed = epq.Editor(idf, idd)

# Do some stuff...
# ================

# Print zone names
mask = ed.mask('Zone')
zone_name = ed.get_field(mask, 'Name')

print('Zone name:\n{}\n'.format(zone_name))

# Print surfaces of the zone
mask = ed.mask('BuildingSurface:Detailed', Zone_Name=zone_name)
surface_names = ed.get_field(mask, 'Name')

print('Surface names:')
for sn in surface_names:
    print(sn)
print('\n')
