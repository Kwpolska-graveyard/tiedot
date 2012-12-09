# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# Tie with a Dot underneath.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    tiedot.TEMPLATE
    ~~~~~~~~~~~~~~~

    TEMPLATE.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""
from . import TDHOME, LOG

try:
    import cPickle as pickle
except ImportError:
    import pickle
