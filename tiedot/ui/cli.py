# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# The Tiedot User Interface.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    tiedot.ui.cli
    ~~~~~~~~~~~~~

    The Tiedot Command-Line Interface.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""
import sys
import getpass
import time
import threading
from .. import LOG
from . import UI


class CLI(UI):
    """The Tiedot Command-Line Interface."""
    pcount = 0
    pcur = 0
    throb = False
    def auth(self):
        """Authenticate."""
        if sys.version_info[0] < 3:
            inp = raw_input
        else:
            inp = input

        u = inp('Username: ')
        p = getpass.getpass('Password: ')
        from .. import AUTH
        from tiedot.auth import AuthError
        try:
            AUTH.auth(u, p)
        except AuthError as e:
            LOG.exception(e)
            print('Authentication Error: {}'.format(e))
            exit(1)

    def passwd(self):
        """Get a password."""
        return getpass.getpass('Password: ')

    def pmsg(self, msg):
        """Print a progress message."""
        self.pcur += 1
        sys.stdout.write('\r')
        ln = len(str(self.pcount))
        if ln < 2:
            ln = 2
        sys.stdout.write(('[{:>' + str(ln) + '}/{:<2}] ').format(self.pcur,
                                                                 self.pcount))
        sys.stdout.write('{:<70}'.format(msg))
        if self.pcur == self.pcount:
            self.pcount = 0
            self.pcur = 0
            print('')

    def _throbber(self, msg, printback=True):
        """Display a throbber."""
        self.throb = True
        while self.throb:
            for i in ('|', '/', '-', '\\'):
                sys.stdout.write('\r[{}] {}'.format(i, msg))
                time.sleep(0.1)
        if not self.throb and printback:
            print('')

    def throbber(self, msg, printback=True):
        """Run the throbber in a thread."""
        threading.Thread(target=self._throbber, args=(msg, printback)).start()
