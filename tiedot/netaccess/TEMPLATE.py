# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# The Tiedot Network Access Services.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.
"""
    tiedot.netaccess.TEMPLATE
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    The Tiedot Network Access Services---TEMPLATE side.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""


import logging
from . import TDHOME

LOG = logging.getlogger('tdna-TEMPLATE')

try:
    import cPickle as pickle
except ImportError:
    import pickle
