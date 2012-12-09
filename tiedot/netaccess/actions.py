# -*- encoding: utf-8 -*-
# Tiedot v0.1.0
# The Tiedot Network Access Services.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.
"""
    tiedot.netaccess.actions
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The Tiedot Network Access actions.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""


class Action(object):
    """A Tiedot Network Access Action."""
    name = None
    ref = None
    queue = []
    commands = set()

class Global(Action):
    """Tiedot global action data."""
    name = 'Global'
    ref = '__global__'
    queue = []
    commands = {'HELLO', 'HOWDY', 'AUTH', 'AUTHSTATUS', 'ACTION', 'ADDUSER',
            'DELUSER', 'CHANGEPWD', 'USERMOD', 'AUTHTR', 'FILES', 'REFUSE',
            'QUIT', 'BYE'}

class Sync(Action):
    """The Sync action."""
    name = 'Sync'
    ref = 'sync'
    queue = []
    commands = {'DIRS', 'CURDATA', 'HAVE', 'WANT', 'DATAEQ'}

class LNA(Action):
    """The Live Network Access (LNA) action."""
    name = 'Live Network Access'
    ref = 'lna'
    queue = []
    commands = {'TREE', 'MKDIR', 'GET', 'PUT', 'REPR'}

class UserMod(Action):
    """The User Modification action."""
    name = 'User Modification'
    ref = 'usermod'
    queue = []
    commands = {'ADDUSER', 'DELUSER', 'CHANGEPWD', 'USERMOD', 'AUTHTR'}

