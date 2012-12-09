# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# Tie with a Dot underneath.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    tiedot.auth
    ~~~~~~~~~~~

    The Tiedot authentication system.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""
from . import TDHOME, LOG, TDError
import tiedot.netaccess.client as naclient
import hashlib
import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

class AuthError(TDError):
    """An authorization error."""
    pass


class Auth(object):
    """Authentication object."""
    def __init__(self):
        """Initialize."""
        self.user = None
        self.passwd = None

    def auth(self, user, passwd):
        """Authenticate."""
        with open(os.path.join(TDHOME, 'data', '__auth__.tdp'), 'rb') as fh:
            users = pickle.load(fh)

        if not user in users:
            raise AuthError('no such user')
        else:
            spwd = hashlib.sha512(passwd.encode('utf-8')).hexdigest()
            if users[user] == spwd:
                self.user = user
                self.passwd = spwd
            elif users[user] == passwd:  # for use by the sync server.
                self.user = user
                self.passwd = passwd
            else:
                raise AuthError('wrong password')

    def logout(self, sf):
        """Log out."""
        if sf == 'TiedotLogout':
            self.user = None
            self.passwd = None
        else:
            raise AuthError('Please use an UI logout function.')

    def test(self):
        """Test the security."""
        if not self.user:
            return True

        with open(os.path.join(TDHOME, 'data', '__auth__.tdp'), 'rb') as fh:
            if pickle.load(fh)[self.user] != self.passwd:
                LOG.error('SECURITY BREACH: Auth got a password set by a human')
                self.logout()
                raise AuthError('SECURITY BREACH.  Logging out.')
            else:
                return True

    def adduser(self, user, passwd, sync=True):
        """Add an user."""
        with open(os.path.join(TDHOME, 'data', '__auth__.tdp'), 'rb') as fh:
            users = pickle.load(fh)

        if user in users:
            raise AuthError('this user already exists')

        spwd = hashlib.sha512(passwd.encode('utf-8')).hexdigest()
        users[user] = spwd
        try:
            if sync:
                naclient.usermod(self, adduser=(user, spwd))
        except:
            raise
        else:
            with open(os.path.join(TDHOME, 'data', '__auth__.tdp'),
                      'wb') as fh:
                pickle.dump(users, fh, protocol=2)

    def deluser(self, user, passwd, sync=True):
        if user == self.user:
            raise AuthError('cannot delete the user you’re logged in as')

        with open(os.path.join(TDHOME, 'data', '__auth__.tdp'), 'rb') as fh:
            users = pickle.load(fh)


        spwd = hashlib.sha512(passwd.encode('utf-8')).hexdigest()

        if users[user] != spwd:
            raise AuthError('wrong password')

        users.pop(user)

        try:
            if sync:
                naclient.usermod(self, deluser=(user, spwd))
        except:
            raise
        else:
            with open(os.path.join(TDHOME, 'data', '__auth__.tdp'),
                      'wb') as fh:
                pickle.dump(users, fh, protocol=2)

    def changepwd(self, oldpasswd, newpasswd, sync=True):
        """Change the password."""
        if not self.user:
            raise AuthError('not logged in')
        elif self.passwd != oldpasswd:
            raise AuthError('wrong password')

        with open(os.path.join(TDHOME, 'data', '__auth__.tdp'), 'rb') as fh:
            users = pickle.load(fh)

        if users[self.user] != oldpasswd:
            LOG.error('SECURITY BREACH: Auth got a password set by a human')
            self.logout()
            raise AuthError('wrong password + SECURITY BREACH.  Logging out.')

        spwd = hashlib.sha512(newpasswd.encode('utf-8')).hexdigest()
        users[self.user] = spwd

        try:
            if sync:
                naclient.usermod(self, changepwd=(oldpasswd, newpasswd))
        except:
            raise
        else:
            with open(os.path.join(TDHOME, 'data', '__auth__.tdp'),
                      'wb') as fh:
                pickle.dump(users, fh, protocol=2)
