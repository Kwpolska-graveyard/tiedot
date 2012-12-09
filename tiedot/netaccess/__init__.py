# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# The Tiedot Network Access Services.
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
    tiedot.netaccess
    ~~~~~~~~~~~~~~~~

    The Tiedot Network Access Services.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""


import os
import base64
import hashlib

try:
    import cPickle as pickle
except ImportError:
    import pickle
from .. import TDHOME, TDError
from tiedot.netaccess import actions

ACTIONS = {'sync': actions.Sync, 'lna': actions.LNA, 'usermod':
        actions.UserMod}

def NAError(TDError):
    """A synchronization error."""
    pass

def unbp(data):
    """Un-(Base64-Pickle)."""
    return pickle.loads(base64.b64decode(data))

def bp(data):
    """Base64-Pickle."""
    return base64.b64encode(pickle.dumps(data, protocol=2))

def getdirs():
    """Get the directory listing BP."""
    _ = len(os.path.join(TDHOME, 'data'))
    return bp([i[_:] for i, j, k in os.walk(os.path.join(TDHOME, 'data'))])

def mkdirs(dbp):
    """Use a Directory Listing BP."""
    for i in unbp(dbp):
        home = os.path.join(TDHOME, 'data')
        try:
            os.makedirs('/'.join((home, i)))
        except OSError:
            pass

def mkdict():
    """Generate a Data Dict BP."""
    dd = {}
    for r, ds, fs in os.walk(os.path.join(TDHOME , 'data', '')):
        for f in fs:
            fp = r + f
            with open(fp, 'rb') as fh:
                buf = fh.read(65536)
                hashf = hashlib.sha1()
                while len(buf) > 0:
                    hashf.update(buf)
                    buf = fh.read(65536)
            dd[f] = {'s': hashf.hexdigest(), 't': os.stat(fp).st_mtime}
    return dd
