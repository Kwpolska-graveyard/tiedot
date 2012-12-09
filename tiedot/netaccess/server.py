# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# The Tiedot Network Access Services.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.
"""
    tiedot.netaccess.server
    ~~~~~~~~~~~~~~~~~~~~~~~

    The Tiedot Network Access Services---server side.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""


import logging
import time
from twisted.internet import protocol, reactor
from tiedot.auth import AuthError
from . import *
from .. import TDHOME, AUTH, CONFIG
LOG = logging.getLogger('tdna-server')

try:
    import cPickle as pickle
except ImportError:
    import pickle

class NAServer(protocol.Protocol):
    def __init__(self, sessions):
        """Initialize Network Access."""
        LOG.debug('TiedotNA initialized.')
        self.sessions = sessions
        self.can_exit = True
        self.lastts = 0
        self.handshake = False

    def connectionMade(self):
        """Start the connection."""
        self.startts = time.time()
        self.replace()
        LOG.info('{}: connected.'.format(self.startts))

    def connectionLost(self, reason):
        LOG.info('{}: connection lost.'.format(self.startts))
        del self.sessions[self.startts]

    def replace(self):
        """Replace ourselves."""
        self.sessions[self.startts] = self

    def bye(self, positive=True):
        """Quit if needed."""
        LOG.info('{}: quitting.  Positive={}.'.format(self.startts,
            positive))

        if positive:
            self.transport.write('BYE {}\n'.format(time.time()))
        else:
            self.transport.write('BYE {}\n'.format(self.lastts))

        self.transport.loseConnection()

    def handle_HELLO(self, data):
        """Handle HELLO."""
        if not self.handshake:
            self.transport.write('HOWDY {}\n'.format(time.time()))
            if data[1:]:
                self.lastts = data[1:]
            else:
                self.lastts = 0
            self.handshake = True
            LOG.info('{}: handshake performed.'.format(self.startts))

    def validate_handshake(self, command):
        """Refuse if no handshake."""
        if not self.handshake:
            self.transport.write('REFUSE {}\n'.format(command))
            return False
        else:
            return True

    def handle_QUIT(self):
        """Handle QUIT."""
        if self.action.ref == 'usermod':
            LOG.debug('Modifying auth data...')
            for data in self.action.queue:
                try:
                    if data[0] == 'ADDUSER':
                        AUTH.adduser(data[1], data[2], sync=False)
                    elif data[0] == 'DELUSER':
                        AUTH.deluser(data[1], data[2], sync=False)
                    elif data[0] == 'CHANGEPWD':
                        AUTH.changepwd(data[1], data[2], sync=False)
                except AuthError as e:
                    if data[0] == 'CHANGEPWD':
                        self.transport.write('REFUSE {}/{}\n'.format(data[0],
                            e))
                    else:
                        self.transport.write('REFUSE {} {}/{}\n'.format(data[0],
                            data[1], e))

            LOG.debug('Auth data modified.')
            self.bye(False)
        elif self.can_exit:
            self.bye(False)
        else:
            self.transport.write('REFUSE QUIT\n')

    def handle_AUTH(self, data):
        """Handle AUTH."""
        if self.validate_handshake('AUTH'):
            self.user = data[0]
            self.passwd = data[1]
            try:
                AUTH.auth(self.user, self.passwd)
                LOG.info('{}: authenticated.'.format(self.startts))
                self.transport.write('AUTHSTATUS 1\n')
            except AuthError as e:
                LOG.exception(e)
                LOG.info('{}: authentication failed.'.format(self.startts))
                self.transport.write('AUTHSTATUS 0\n')
                self.bye(False)

    def handle_ACTION(self, data):
        """Handle a new action to use."""
        self.action = ACTIONS[data.lower()]()
        if self.action.ref == 'sync':
            LOG.info('Protocol set to sync.')
            self.transport.write('DIRS {}\n'.format(getdirs()))
        elif self.action.ref == 'lna':
            LOG.info('Protocol set to lna.')
            self.transport.write('TREE {}\n'.format(bp(None)))  # TODO
        elif self.action.ref == 'usermod':
            LOG.info('Protocol set to usermod.')

    def handle_USERMOD(self, data):
        """Handle user modification."""
        if self.validate_handshake('USERMOD'):
            if self.action.ref == 'usermod':
                self.action.queue.append((data[0], data[1], data[2]))
            else:
                try:
                    if data[0] == 'ADDUSER':
                        AUTH.adduser(data[1], data[2], sync=False)
                    elif data[0] == 'DELUSER':
                        AUTH.deluser(data[1], data[2], sync=False)
                    elif data[0] == 'CHANGEPWD':
                        AUTH.changepwd(data[1], data[2], sync=False)
                    else:
                        self.transport.write('USERMOD 0\n')
                except AuthError:
                    self.transport.write('USERMOD 0\n')
                else:
                    self.transport.write('USERMOD 1\n')
                finally:
                    self.bye(False)

    def handle_CURDATA(self, data):
        """Handle CURDATA."""
        if self.validate_handshake('CURDATA'):
            our = mkdict()
            their = unbp(data)
            # III.3. Data Comparison Procedure.
            itms = []
            have = []
            want = []
            none = []
            # III.3.1. Compare items.
            for i, j in our.items():
                itms.append(i)
                if i not in their:
                    their[i] = {'t': 0, 's': '0'}

            for i, j in their.items():
                if i not in our:
                    our[i] = {'t': 0, 's': '0'}

            # III.3.2. Iterate over items.
            for i, j in our.items():
                # III.3.2.a. Add the item to ->ITMS.
                itms.append(i)

                # III.3.2.b. Compare checksums.
                if our[i]['s'] != their[i]['s']:
                    # III.3.2.b.ii. ≠ Compare timestamps.
                    ot = our[i]['t']
                    tt = their[i]['t'] + self.timediff
                    if ot < tt:
                        # III.3.b.ii.B. S < C ->WANT.
                        want.append(i)
                    else:
                        # III.3.b.ii.A. S > C ->HAVE.
                        # III.3.b.ii.C. S = C Kill somebody and assume ->HAVE.
                        have.append(i)
                else:
                    # III.3.2.a = ->NONE.
                    none.append(i)
            itemset = set(itms)
            altiset = set(have + want + none)
            if itemset != altiset:
                diff = [i for i in itemset if i not in altiset]
                LOG.error('{}: Somehow, we missed the following items: '
                        '{}'.format(self.startts, diff))

            if '__auth__.tdp' in want:
                # __auth__.tdp cannot be transported for safety reasons.
                want.remove('__auth__.tdp')
                have.append('__auth__.tdp')
                self.transport.write('AUTHTR\n')

            self.transport.write('HAVE {}\nWANT {}\n'.format(bp(have),
                bp(want)))
            havef = {}
            for i in have:
                with open(os.path.join(TDHOME, 'data', i), 'rb') as fh:
                    havef[i] = base64.b64encode(fh.read())

            self.transport.write('FILES HAVE {}\n'.format(bp(havef)))

    def handle_WANT(self, data):
        """Handle WANT."""
        for i, j in unbp(data).items():
            with open(os.path.join(TDHOME, 'data', i), 'wb') as fh:
                fh.write(base64.b64decode(j))
        self.bye(True)

    def dataReceived(self, data):
        sdata = data.strip().split('\n')
        for i in sdata:
            LOG.debug('{}: {}'.format(self.startts, i))
            i = i.split(' ')
            if i[0] == 'HELLO':
                self.handle_HELLO(i[1:])
            elif i[0] == 'AUTH':
                self.handle_AUTH(i[1:])
            elif i[0] == 'ACTION':
                self.handle_ACTION(i[1])
            elif i[0] in ['ADDUSER', 'DELUSER', 'CHANGEPWD']:
                self.handle_USERMOD(i)
            elif i[0] == 'TIMEDIFF':
                self.timediff = float(i[1])
            elif i[0] == 'CURDATA':
                self.handle_CURDATA(i[1])
            elif i[0] == 'FILES':
                if i[1].startswith('WANT'):
                    self.handle_WANT(i[2])
            elif i[0] == 'QUIT':
                self.handle_QUIT()
            else:
                self.transport.write(' '.join(['?'] + i) + '\n')

class NAFactory(protocol.Factory):
    sessions = {}
    def buildProtocol(self, addr):
        return NAServer(self.sessions)

def run(port):
    """Run the daemon."""
    reactor.listenTCP(port, NAFactory())
    LOG.info('*** Tiedot NA Server starting @ port {}.'.format(port))
    reactor.run()

if __name__ == '__main__':
    run()
