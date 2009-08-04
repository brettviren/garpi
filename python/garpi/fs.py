#!/usr/bin/env python
'''
Directory layout

This module provides definitions of directories.  

It also provides goto/goback to change the current working directory
of the application.  Client code should prefer to pass target
directories to the applicable function from the "command" module.

'''

from config import cli

def external():
    'Return the absolute path to the directory holding the external packages'
    return cli.opts.base_directory + '/external'

def projects():
    'Return the absolute path to the directory holding the projects'
    return cli.opts.base_directory + '/' + cli.opts.name

def setup():
    'Return the absolute path to the directory holding the setup scripts'
    return projects() + '/setup'

from util import log
from exception import CommandFailure
import os


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
    log.info('goto %s'%theDir)
    return dirStack
    
def goback():
    'Return the the most recent directory from which a goto() was issued'
    if not dirStack:
        log.warning('Directory stack empty')
        return
    theDir = dirStack.pop()
    os.chdir(theDir)
    return theDir
