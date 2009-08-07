#!/usr/bin/env python

'''
Sanity checks of the installation host
'''

from util import log
from command import cmd
import os

def check_generic():
    return True

def check_redhat():
    return True

def check_debian():
    arch = cmd('dpkg --print-architecture',output=True).strip()
    mach = cmd('uname -m',output=True).strip()
    if arch == 'i386' and mach == 'x86_64':
        log.warning('''Your kernel claims to be x86_64 but your user space claims to be i386.  This will greatly confuse the various build systems.  To work around this issue, either install an i686 kernel or run "linux32 /bin/bash" before installing or running the code.''')
        return False
    return True


def check():
    '''Perform sanity checks relevant to the installation host'''

    assert check_generic(), 'Generic sanity checks failed.'

    if os.path.exists('/etc/debian_version'):
        assert check_debian(), 'Debian specific checks failed.'
    if os.path.exists('/etc/redhat-release'):
        assert check_redhat(), 'Red Hat specific checks failed.'

    return True
