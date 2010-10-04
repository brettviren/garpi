#!/usr/bin/env python

'''
Sanity checks of the installation host
'''

from util import log
from command import cmd
import os

def check_generic():

    try:
        cfg = os.environ['CMTCONFIG']
    except KeyError,err:
        print '''
        It is required to set CMTCONFIG by hand.
        Use cmtconfig.py to provide a suggestion.
'''
        return False

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

def check_external():
    'If non-standard external location, make sure it is symlinked'
    from config import cli
    import fs
    path = fs.external()
    extdir = os.path.basename(path)
    base = os.path.dirname(path)
    target = os.path.join(cli.cwd,'external')

    # standard name, standard location
    if extdir == 'external' and os.path.samefile(cli.cwd,base):
        return True
    
    if os.path.exists(target):
        if os.path.islink(target):
            os.remove(target)
        else:
            log.error('External directory is "%s" but need to symlink it from "%s" which is in the way'%(path,target))
            return False
        
    log.info('Making symlink from "%s" to "%s"'%(path,target))
    os.symlink(path,target)
    return True


def check():
    '''Perform sanity checks relevant to the installation host'''

    #assert check_generic(), 'Generic sanity checks failed.'

    if os.path.exists('/etc/debian_version'):
        assert check_debian(), 'Debian specific checks failed.'
    if os.path.exists('/etc/redhat-release'):
        assert check_redhat(), 'Red Hat specific checks failed.'
    assert check_external(), 'Sanity check on external directory failed.'
    return True
