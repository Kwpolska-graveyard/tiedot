# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# Tie with a Dot underneath.
# Copyright © 2012, Kwpolska.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the author of this software nor the names of
#    contributors to this software may be used to endorse or promote
#    products derived from this software without specific prior written
#    consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
    tiedot
    ~~~~~~

    Tie with a Dot underneath.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""
from __future__ import (absolute_import, division, print_function,
        unicode_literals)
import logging
import os
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    import cPickle as pickle
except ImportError:
    import pickle

__version__ = '0.1.0'
TDHOME = os.getcwd()
logging.basicConfig(format='%(asctime)-15s [%(levelname)-7s] '
                    ':%(name)-10s: %(message)s',
                    filename=os.path.join(TDHOME, 'aux', 'tiedot.log'),
                    level=logging.DEBUG)
LOG = logging.getLogger('tiedot')
LOG.info('*** Tiedot v' + __version__)

class TDError(Exception):
    """A Tiedot Error."""
    pass

CONFIG = configparser.ConfigParser()
with open(os.path.join(TDHOME, 'aux', 'tiedot.cfg')) as fh:
    CONFIG.readfp(fh)
from .ui.cli import CLI
UI = CLI()
from . import auth
AUTH = auth.Auth()

if not sys.version.startswith('2.7'):
    raise TDError('Python 2.7.x required.')
    sys.exit(1)

class Object(object):
    """A common class for every Tiedot object."""
    def __repr__(self):
        """Because <tiedot.Object object> is too mainstream."""
        try:
            tdr = self.tdr
        except AttributeError:
            tdr = 'None'

        try:
            name = self.name
        except AttributeError:
            name = 'Tiedot Object'

        try:
            __path__ = self.__path__
        except AttributeError:
            __path__ = '<mem>'

        return '{}/{} @ {}'.format(tdr, name, __path__)

    def get(self, obj):
        """Handle data retrieval."""
        if isinstance(obj, SubAttr):
            return obj.__value__
        else:
            return obj

    def __setattr__(self, name, value):
        """Handle saving.  May be tricky!"""
        super(Object, self).__setattr__(name, value)
        try:
            path = self.__path__.replace('.', '/')
            pathd = '/'.join(path.split('/')[:-1])
            if '/' in path:
                try:
                    os.makedirs(os.path.join(TDHOME, 'data', pathd))
                except:
                    pass
            with open(os.path.join(TDHOME, 'data', path + '.tdp'), 'wb') as fh:
                pickle.dump(self, fh, protocol=2)
        except AttributeError:
            LOG.error('Cannot save -- no filename. {}'.format(self))


class SubAttr(object):
    """A subattribute for Tiedot objects."""
    def __init__(self, initattr):
        """Initialize the attribute."""
        self.value = initattr

    def __repr__(self):
        """Reproduce."""
        return self.value

    def __str__(self):
        """Stringize."""
        return self.value

    def __unicode__(self):
        """Unicode.  (py2k)"""
        return self.value


def addtdr(obj):
    """Add a TDR."""
    with open(os.path.join(TDHOME, 'data', '__tdr__.tdp'), 'rb') as fh:
        tdr = pickle.load(fh)

    tdr.update({obj.tdr: obj.__path__})

    with open(os.path.join(TDHOME, 'data', '__tdr__.tdp'), 'wb') as fh:
        pickle.dump(tdr, fh, protocol=2)

    return {'tdr': tdr, obj.tdr: obj}

def deltdr(obj):
    """Delete a TDR."""
    global tiedot
    with open(os.path.join(TDHOME, 'data', '__tdr__.tdp'), 'rb') as fh:
        tdr = pickle.load(fh)

    tdr.pop(obj.tdr)

    with open(os.path.join(TDHOME, 'data', '__tdr__.tdp'), 'wb') as fh:
        pickle.dump(tdr, fh, protocol=2)

    return {'tdr': tdr, obj.tdr: None}

def rehash():
    """Rehash the config."""
    with open(os.path.join(TDHOME, 'aux', 'tiedot.cfg')) as fh:
        return configparser.ConfigParser().readfp(fh)

def getobjects():
    """Get all the objects."""
    out = Object()
    out.name = 'ROOT'
    if not AUTH.user:
        from tiedot.auth import AuthError
        LOG.error('SECURITY BREACH.  getobjects() without login')
        raise AuthError('SECURITY BREACH.')
        exit(1)
        return {}

    for root, dirs, files in os.walk(os.path.join(TDHOME, 'data')):
        rt = root[len(os.path.join(TDHOME, 'data')):]
        if rt == '':
            for i in files:
                if not i.startswith('__') and not i.endswith('__.tdp'):
                    with open(os.path.join(root, i), 'rb') as fh:
                        _ = pickle.load(fh)
                    setattr(out, _.__path__, _)
        else:
            for i in files:
                with open(os.path.join(root, i), 'rb') as fh:
                    _ = pickle.load(fh)
                if _.__path__.endswith('.__'):
                    path = _.__path__[:-3]
                else:
                    path = _.__path__

                ps = path.split('.')
                j = out
                for pi in ps:
                    try:
                        j = getattr(j, pi)
                    except AttributeError:
                        if pi == ''.join(ps[-1:]):
                            setattr(j, pi, _)
                        elif '__.tdp' in files:
                            with open(os.path.join(root, '__.tdp'), 'rb') as fh:
                                orig = pickle.load(fh)
                            setattr(j, pi, orig)
                        else:
                            ph = Object()
                            ph.name = 'placeholder'
                            setattr(j, pi, ph)

                        j = getattr(j, pi)

    # TDR.
    with open(os.path.join(TDHOME, 'data', '__tdr__.tdp'), 'rb') as fh:
        tdr = pickle.load(fh)

    for i, j in tdr.items():
        if j.endswith('.__'):
            j = j[:-3]
        r = getattr(out, j.split('.')[0])

        for k in j.split('.')[1:]:
            r = getattr(r, k)

        tdr.update({i: r})

    setattr(out, 'tdr', tdr)

    for i, j in tdr.items():
        setattr(out, i, j)
    return out.__dict__
