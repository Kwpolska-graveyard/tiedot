# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# The Tiedot Network Access Services.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    tiedot.netaccess.client
    ~~~~~~~~~~~~~~~~~~~~~~~

    The Tiedot Network Access Services---client side.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""
import logging
import time
import sys
from twisted.internet import protocol, reactor, endpoints
from . import *
from .. import CONFIG

LOG = logging.getLogger('tdna-client')

try:
    import cPickle as pickle
except ImportError:
    import pickle

class NAClient(protocol.Protocol):
    """A client object."""
    def __init__(self, auth, action, requests):
        """Grab the authentication details."""
        self.auth = auth
        self.action = ACTIONS[action]()
        self.requests = requests

    def hello(self):
        """Say HELLO to the server."""
        self.transport.write('HELLO {}\n'.format(CONFIG.get('naclient',
            'ts')))

    def handle_HOWDY(self, data):
        """Handle a server’s greeting."""
        self.startts = float(data)
        self.timediff = int(time.time() - self.startts)
        self.transport.write('TIMEDIFF {}\nAUTH {} {}\n'.format(self.timediff,
            self.auth.user, self.auth.passwd))

    def handle_DIRS(self, data):
        """Handle DIRS."""
        mkdirs(data)
        self.transport.write('CURDATA {}\n'.format(bp(mkdict())))

    def handle_HAVE(self, data):
        """Handle a HAVE."""
        for i, j in unbp(data).items():
            with open(os.path.join(TDHOME, 'data', i), 'wb') as fh:
                fh.write(base64.b64decode(j))

        wantf = {}

        for i in self.want:
            with open(os.path.join(TDHOME, 'data', i), 'rb') as fh:
                wantf[i] = base64.b64encode(fh.read())

        self.transport.write('FILES WANT {}\n'.format(bp(wantf)))

    def dataReceived(self, data):
        """Handle incoming data."""
        sdata = data.strip()
        sdata = sdata.split('\n')
        for i in sdata:
            LOG.debug('IN: {}'.format(i))

            i = i.split(' ')
            if i[0] == 'HOWDY':
                self.handle_HOWDY(i[1])
            elif i[0] == 'AUTHSTATUS':
                if i[1] == '1':
                    self.transport.write('ACTION {}\n'.format(
                        self.action.ref.upper()))
                    if self.action.ref == 'usermod':
                        for i, j in self.requests.items():
                            self.transport.write(' '.join([i.upper()] +
                                list(j)) + '\nQUIT\n')
                else:
                    LOG.error('Authentication failed.')
            elif i[0] == 'DIRS':
                self.handle_DIRS(i[1])
            elif i[0] == 'HAVE':
                self.have = unbp(i[1])
            elif i[0] == 'WANT':
                self.want = unbp(i[1])
            elif i[0] == 'FILES':
                if i[1].startswith('HAVE'):
                    self.handle_HAVE(i[2])
            elif i[0] == 'BYE':
                CONFIG.set('naclient', 'ts', int(float(i[1])))
                with open(os.path.join(TDHOME, 'aux', 'tiedot.cfg'), 'w') as fh:
                    CONFIG.write(fh)
                LOG.info('Done in {} seconds.'.format(str(float(i[1]) -
                    self.startts)))
                reactor.stop()

class NA(protocol.ClientFactory):
    """A client factory."""
    def __init__(self, auth, action, requests={}):
        """Share the authentication."""
        self.auth = auth
        self.action = action
        self.requests = requests

    def startedConnecting(self, connector):
        """Inform that a connection has been started."""
        LOG.info('Connecting...')
        sys.stdout.write('Connecting... ')

    def buildProtocol(self, addr):
        """Inform that we are done connecting."""
        LOG.info('Connected.')
        c = NAClient(self.auth, self.action, self.requests)
        c.factory = self
        return c

    def clientConnectionLost(self, connector, reason):
        """Retry after a lost connection."""
        LOG.error('Lost connection.  Reason: {}'.format(reason))
        print('Lost connection.  Reason: {}'.format(reason))
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        """Inform that the connection failed."""
        LOG.error('Connection failed.  Reason: {}'.format(reason))
        print('Connection failed.  Reason: {}'.format(reason))
        reactor.stop()

def greet(p):
    """Start everything."""
    p.hello()

def sync(conf):
    """Run sync."""
    auth, addr, port = conf
    point = endpoints.TCP4ClientEndpoint(reactor, addr, port)
    d = point.connect(NA(auth, 'sync'))
    d.addCallback(greet)
    reactor.run()

def lna(conf):
    """Run LNA."""
    raise NotImplementedError
    #point = endpoints.TCP4ClientEndpoint(reactor, CONFIG.get('naclient',
            #'server'), int(CONFIG.get('naclient', 'port')))
    #d = point.connect(NA(auth, 'sync'))
    #d.addCallback(greet)
    #reactor.run()

def usermod(conf, **requests):
    """Run User Modification."""
    auth, addr, port = conf
    point = endpoints.TCP4ClientEndpoint(reactor, addr, port)
    d = point.connect(NA(auth, 'usermod', requests))
    d.addCallback(greet)
    reactor.run()
