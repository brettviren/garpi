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

def source (filename,env=None,dir=None,output=False):
    '''Produce a dictionary holding environment variables after the
    given file has been "sourced" and starting with optional initial
    environment in the given env.  If output is False, return only
    this dictionary, if True return a tuple with this dictionary and a
    string containing any output from the source command.'''

    if dir is None:
        dir = os.getcwd()

    fullpath = os.path.join(dir,filename)

    #print fullpath

    if not os.path.exists(fullpath):
        msg = 'no such file: "%s" in "%s"'%(filename,dir)
        log.error(msg)
        raise ValueError,msg

    log.info('sourcing %s in %s'%(filename,dir))
    magic='magic%dmagic'%os.getpid()
    sourcer = os.path.dirname(__file__) + '/source.sh'
    cmdstr = "%s %s %s"%(sourcer,filename,magic)
    cmdres = cmd(cmdstr,env,dir,True,loglevel=log.DEBUG)

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

    if output: return (newenv,'\n'.join(res))
    return newenv


def make(target='',env=None,dir=None,output=False):
    'Make the given target'
    return cmd('make %s'%target,env,dir,output)

def cmd(cmdstr,env=None,dir=None,output=False,loglevel=log.INFO):
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

    Passing loglevel to set at what level the output should be logged.

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
    #print 'cmdstr="%s", env=%s'%(cmdstr,env)

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

        if line:
            line = line.strip()
            log.log(loglevel,line)
            if output:
                out.append(line)

        if res is None: continue
        # fixme: clean up this cut-and-paste of above!
        for line in proc.stdout.readlines():
            if line:
                line = line.strip()
                log.log(loglevel,line)
                if output:
                    out.append(line)
        break

    log_maker.set_format(old_format)

    # Check return code
    if res is not 0:
        if dir: fs.goback()
        else: dir = os.getcwd()
        if isinstance(cmdstr,list): cmdstr = " ".join(cmdstr)
        err = 'Command: "%s" failed with code %d run from directory "%s"'%(cmdstr,res,dir)
        log.error(err)
        log.error('START ENV DUMP:')
        envdump = []
        for k,v in env.items():
            envdump.append('%s=%s'%(k,v))
        log.error('\n%s\nEND ENV DUMP:'%'\n'.join(envdump))
        from exception import CommandFailure
        raise CommandFailure,err

    if dir: fs.goback()
    return '\n'.join(out)
