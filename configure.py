#!/usr/bin/python2
# Tiedot Configure.
import sys
import os
import pickle
import re
import time
import hashlib
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

dirs = ['aux', 'data']
efiles = ['aux/tiedot.log']
count = 13
cur = 0

if sys.version_info[0] < 3:
    inp = raw_input
else:
    inp = input

def pmsg(msg):
    """Write a progress message."""
    global cur
    global count
    cur += 1
    sys.stdout.write('\r')
    sys.stdout.write('[{:>2}/{:<2}] '.format(cur, count))
    sys.stdout.write('{:<70}'.format(msg))
    time.sleep(0.02)

pmsg('Configuring...')
pmsg('Creating directories...')

for i in dirs:
    try:
        os.mkdir(i)
        pmsg('File created: \'{}\''.format(i))
    except IOError as e:
        pmsg(e.strerror + ': \'{}\''.format(e.filename))
    except OSError as e:
        pmsg(e.strerror + ': \'{}\''.format(e.filename))
    except Exception as e:
        pmsg(e)
        print('')

pmsg('Creating files...')

for i in efiles:
    if not os.path.exists(i):
        with open(i, 'w') as fh:
            fh.write('')
        pmsg('File created: \'{}\''.format(i))
    else:
        pmsg('File exists: \'{}\''.format(i))

if not os.path.exists(os.path.join('data', '__tdr__.tdp')):
    with open(os.path.join('data', '__tdr__.tdp'), 'wb') as fh:
        pickle.dump({}, fh, protocol=2)

    pmsg('File created: \'{}\''.format('data/__tdr__.tdp'))
else:
    pmsg('File exists: \'{}\''.format('data/__tdr__.tdp'))

pmsg('Creating user accounts...')
if not os.path.exists(os.path.join('data', '__auth__.tdp')):
    with open(os.path.join('data', '__auth__.tdp'), 'wb') as fh:
        pickle.dump({'tiedot':
                     hashlib.sha512('tiedot'.encode('utf-8')).hexdigest()}, fh,
                    protocol=2)

    pmsg('File created: \'{}\''.format('data/__auth__.tdp'))
    madeauth = True
else:
    pmsg('File exists: \'{}\''.format('data/__auth__.tdp'))
    madeauth = False

pmsg('Tiedot successfully configured.')

print('\n')

print("""

Username: tiedot
Password: tiedot

Please use UI.adduser() and then UI.deluser() as soon as possible.""")
