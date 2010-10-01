#!/usr/bin/env python
'''
Project functions to run subprocess commands and modify environment
through sourcing shell scripts.
'''

import os

def cmd(cmdstr,env=None,path=None):
    '''Run a command with optional environment, maybe changing
    directory to given path.  The a (stdout,stderr) tuple is returned'''

    # Convert to list if given a string
    if type(cmdstr) == type(""):
        cmdstr = cmdstr.strip()
        cmds = cmdstr.split()
        if len(cmds) > 1: cmdstr = cmds

    if not env: env = os.environ

    cwd = None
    if path: 
        cwd = os.getcwd()
        os.chdir(path)
        env['PWD'] = os.getcwd()

    from subprocess import Popen, PIPE, STDOUT
    try:
        proc = Popen(cmdstr,stdout=PIPE,stderr=STDOUT,universal_newlines=True,env=env)
    except OSError,err:
        if cwd: 
            os.chdir(cwd)
            env['PWD'] = cwd
        raise

    res = proc.communicate()
    if proc.returncode < 0:
        raise OSError,'%s failed with %d'%(" ".join(cmdstr),proc.returncode)

    if path:
        os.chdir(cwd)
        env['PWD'] = cwd
    return res


def source (filename,env=None,path=None,output=False):
    '''Produce a dictionary holding environment variables after the
    given file has been "sourced" and starting with optional initial
    environment in the given env.  If output is False, return only
    this dictionary, if True return a tuple with this dictionary and a
    string containing any output from the source command.'''

    import tempfile

    magic='magic%dmagic'%os.getpid()
    (fp,sourcer) = tempfile.mkstemp()
    fp = os.fdopen(fp,"w")
    fp.write('''#!/bin/sh
file=$1 ; shift
delim=$1
if [ -z "$file" ] ; then
    echo "No file given to source"
    exit 1
fi
if [ ! -f "$file" ] ; then
    echo "No such file: $file"
    exit 1
fi
. $file && echo $delim && env
''')
    fp.close()
    os.chmod(sourcer,0700)
    cmdstr = "%s %s %s"%(sourcer,filename,magic)
    cmdres,stderr = cmd(cmdstr,env,path)
    os.remove(sourcer)

    res = []
    newenv = {}
    inenv = False
    for line in cmdres.split('\n'):
        line = line.strip()
        if not line: continue

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

    if path: newenv['PWD'] = os.getcwd()

    if output: return (newenv,'\n'.join(res))
    return newenv
