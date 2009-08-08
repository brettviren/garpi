#!/usr/bin/env python
'''
Directory layout

This module provides definitions of directories.  

It also provides goto/goback to change the current working directory
of the application.  Client code should prefer to pass target
directories to the applicable function from the "command" module.

'''

import os

def base():
    'Return the absolute path to the base directory'
    from config import cli
    return cli.opts.base_directory
    
def name():
    'Return the name of the release being built'
    from config import cli
    return cli.opts.name

def external():
    'Return the absolute path to the directory holding the external packages'
    return os.path.join(base(),'external')

def projects():
    'Return the absolute path to the directory holding the projects'
    return os.path.join(base(), name())

def setup():
    'Return the absolute path to the directory holding the setup scripts'
    return os.path.join(projects(), 'setup')

from util import log
from exception import CommandFailure


dirStack = []

def assure(theDir):
    'Assure the given directory exists.  Return True if it needed creating'
    if os.path.exists(theDir): return False
    log.info('Creating directory: '+theDir)
    os.makedirs(theDir)
    return True

def goto(theDir,mkdir=True):
    '''Move the application to the given directory.  If mkdir is true,
    any missing path segments will be created.'''
    if not os.path.exists(theDir):
        if mkdir:
            assure(theDir)
        else:
            raise CommandFailure,'Can not goto missing directory: "%s"'%theDir

    dirStack.append(os.getcwd())
    os.chdir(theDir)
    log.debug('goto %s'%theDir)
    return dirStack
    
def goback():
    'Return the the most recent directory from which a goto() was issued'
    if not dirStack:
        log.warning('Directory stack empty')
        return
    theDir = dirStack.pop()
    os.chdir(theDir)
    log.debug('goback to %s'%theDir)
    return theDir
