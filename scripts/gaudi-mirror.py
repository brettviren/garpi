#!/usr/bin/env python

'''
Manage the Git mirror of Gaudi's upstream SVN.

Usage: gaudi-mirror.py [opts] [command]

Logging is saved to a 'garpi.log' file in the CWD.

Commands are:

 init - initialize the mirror, downloading history from SVN (takes long time)

Options

-u|--url 

 Set the URL from which this repository can be accessed.  It is needed
 to properly setup the git submodules.  It will default to
 ssh://`hostname`/`pwd`


'''

import os,sys
from garpi.command import cmd
from garpi.util import log
from garpi import fs

all_packages = ["Gaudi",
                "GaudiAlg",
                "GaudiAud",
                "GaudiExamples",
                "GaudiGSL",
                "GaudiGridSvc",
                "GaudiKernel",
                "GaudiMonitor",
                "GaudiPolicy",
                "GaudiPoolDb",
                "GaudiPython",
                "GaudiRelease",
                "GaudiSvc",
                "GaudiSys",
                "GaudiUtils",
                "HbookCnv",
                "PartPropSvc",
                "RootHistCnv",
                ]



def init_pkg(url,pkg):
    log.info('Initializing %s'%pkg)

    if not os.path.exists(pkg): os.mkdir(pkg)
    fs.goto(pkg)

    if not os.path.exists('.git'): 
        url = 'https://svnweb.cern.ch/guest/gaudi/packages/%s'%pkg
        cmd('git-svn init -s --prefix=upstream-svn/ %s'%url)
        cmd('git-svn fetch')

    fs.goback()
    if not os.path.exists('.git'): cmd('git init')

    def need_add():
        if os.path.exists('.gitmodules'):
            fp = open(".gitmodules")
            lines = map(lambda x: x.strip(), fp.readlines())
            if '[submodule "%s"]'%pkg in lines: return False
        return True
    if need_add():
        cmd('git submodule add %s/%s %s'%(url,pkg,pkg))
        
    fp = open('.git/config')
    lines = map(lambda x: x.strip(), fp.readlines())
    if not '[submodule "%s"]'%pkg in lines:
        cmd('git submodule init %s'%pkg)


    cmd('git add %s'%pkg)

    return

def update_local_branches_pkg(pkg):
    fs.goto(pkg)
    lbranches = []
    rbranches = []
    branches = cmd('git branch -a',output=True).split('\n')

    prefix='upstream-svn/tags/'

    for branch in branches:
        branch = branch.strip()
        if not branch: continue
        if branch[0] == '*': branch = branch[2:]
        if branch[0:len(prefix)] == prefix:
            rbranches.append(branch)
        elif '/' not in branch:
            lbranches.append(branch)
        continue

    for rbranch in rbranches:
        tag = rbranch[len(prefix):]
        if tag in lbranches: continue
        cmd('git checkout -t -b %s %s'%(tag,rbranch))

    cmd('git checkout upstream-svn-trunk')
    fs.goback()

def init(url,pkgs = all_packages):
    for pkg in pkgs: init_pkg(url,pkg)

def update_local_branches(pkgs = all_packages):
    for pkg in pkgs: update_local_branches_pkg(pkg)    

def default_url():
    import socket,os
    host = socket.getfqdn()
    cwd = os.getcwd()
    return 'ssh://%s%s'%(host,cwd)

if '__main__' == __name__:
    from optparse import OptionParser
    parser = OptionParser(usage = __doc__)
    parser.add_option('-u','--url',type='string',default=default_url(),
                      help='Base URL from which this repository may be accessed.')
    opts,args = parser.parse_args(args=sys.argv)
        
    if not args[1:]: 
        parser.print_help()
        sys.exit(1)

    if args[1] == "init": init(opts.url,args[2:] or all_packages)
    if args[1] == "update_local_branches": update_local_branches()


