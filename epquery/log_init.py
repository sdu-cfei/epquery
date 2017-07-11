"""
Copyright (c) 2017, University of Southern Denmark
All rights reserved.

This code is licensed under BSD 2-clause license.
See LICENSE file in the project root for license terms.

Module description
==================
Initializes logger. Should be imported from main module.
"""
import logging

logging.basicConfig(filename='epquery.log', filemode='w', level='DEBUG',
                    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
