#!/usr/bin/env python
'''
A suite of functions to run commands under shell.

All command functions take these optional a keyword arguments;

 env - specify what environment in which to run the given command.  It
       defaults to whatever environment the main program was run from.

 dir - specify from what directory the command should be run.  The
       application will change to that directory, run the command and
       change back.  Default is current working directory.

 output - if True, will return the standard output and error as a
          string.  Default is False.

Client code should prefer to use specific functions to run specific
commands and avoid running the generic cmd() function.
'''

import os
import fs
from util import log

def source(filename,env=None,dir=None,output=False):
    '''Produce a dictionary giving environment variables after the
    given file has been "sourced", starting with the given env or the
    default one in which the application runs.  If output is False,
    return this dictionary, if True return a tuple with this
    dictionary and a string containing any output from the source
    command.'''


    if dir: fs.goto(dir)

    log.info('sourcing %s in %s'%(filename,os.getcwd()))

    magic='magic%dmagic'%os.getpid()
    cmdstr = ". %s && echo '%s' && env"%(filename,magic)
    import commands

    ret,cmdres = commands.getstatusoutput(cmdstr)

    if ret != 0:
        from exception import CommandFailure
        err = 'Failed to source "%s" from %s:\n%s' \
            %(filename,os.getcwd(),cmdres)
        if dir: fs.goback()
        log.error(err)
        raise CommandFailure, err

    if dir: fs.goback()

    res = []
    newenv = {}
    inenv = False
    for line in cmdres.split('\n'):
        if line == magic:
            inenv = True
            continue
        if inenv:
            ind = line.find('=')
            key = line[:ind]
            val = line[ind+1:]
            newenv[key] = val
        else:
            res.append(line)
        continue

    if env:
        env.update(newenv)
    else:
        env = newenv
    if output: return (env,'\n'.join(res))
    return env


def make(target='',env=None,dir=None,output=False):
    'Make the given target'
    return cmd('make %s'%target,env,dir,output)

def cmd(cmdstr,env=None,dir=None,output=False):
    '''
    Run an arbitrary command given by first non-optional argument.  If
    it is a full command line string it will be broken down via a
    split() on spaces.  If spaces are meaningful, pass in a list of
    strings.

    If env is defined it will be set the environment in which the
    command is run.

    If dir is set the command will be run after going to that
    directory.

    If output is True, the stdout/stderr will be returned as a string.

    Avoid calling this function in favor of specific command function
    '''
    out = []

    # Convert to list if given a string
    if type(cmdstr) == type(""):
        cmdstr = cmdstr.strip()
        cmds = cmdstr.split()
        if len(cmds) > 1: cmdstr = cmds

    if not env: env = os.environ

    from subprocess import Popen, PIPE, STDOUT

    if dir: fs.goto(dir)

    log.info('running: "%s" in %s'%(cmdstr,os.getcwd()))

    # Must update this explicitly since env is not tied to this
    # application's env.
    env['PWD'] = os.getcwd()

    #log.info('\n'.join(map(lambda x: '"%s" --> "%s"'%x, env.iteritems())))

    # Start the command
    # print 'cmdstr="%s", env=%s'%(cmdstr,env)
    try:
        proc = Popen(cmdstr,stdout=PIPE,stderr=STDOUT,universal_newlines=True,env=env)
    except OSError,err:
        if dir: fs.goback()
        log.error_notrace(err)
        log.error_notrace('In directory %s'%os.getcwd())
        raise

    # Convert to simple format
    from util import log_maker
    old_format = log_maker.set_format('%(message)s')

    # Read in and dump output until command finishes
    res = None
    while True:
        line = proc.stdout.readline()

        res = proc.poll()

        line = line.strip()
        log.info(line)
        if output:
            out.append(line)

        if res is None: continue
        break

    log_maker.set_format(old_format)

    # Check return code
    if res is not 0:
        if dir: fs.goback()
        if type(cmdstr) == list: cmdstr = " ".join(cmd)
        err = 'Command: %s failed with code %d'%(cmd,res)
        log.error(err)
        from exception import CommandFailure
        raise CommandFailure,err

    if dir: fs.goback()
    return '\n'.join(out)
