#!/usr/bin/env python

'''
Thin functional wrapper over the git programs
'''

from util import untar, log
from command import cmd
import os, fs

def ver():
    from config import cli
    return cli.file.get('git','git_version')

def tgz():
    return "git-%s.tar.gz"%ver()

def base_url():
    from config import cli
    return cli.file.get('git','git_site_url')

def url():
    return '%s/%s'%(base_url(),tgz())

def srcdir():
    return os.path.join(fs.external(),'git-%s'%ver())

def prefix():
    import cmt
    return os.path.join(fs.external(),'git',ver(),cmt.macro('tag').strip())

_gitexe = None
def gitexe():
    global _gitexe
    if not _gitexe:
        _gitexe = os.path.join(prefix(),'bin/git')
        #print 'setting gitexe to',_gitexe
    return _gitexe

def download():
    'Download GIT source tar file into external area.'
    log.info('downloading git tar file')
    target = os.path.join(fs.external(),tgz())
    from get import get
    from exception import InconsistentState
    target = get(url(),target)
    if not os.path.exists(target):
        raise InconsistentState,'Tar file does not exist: %s%s'%(os.getcwd(),tgz())
    return target

def unpack():
    'Unpack the previously downloaded tarfile'
    log.info('unpacking git source')
    target = srcdir()
    if os.path.exists(target):
        log.info('git appears to already be unpacked in %s'%(target))
        return target
    fs.goto(fs.external(),True)
    untar(tgz())
    return target

def build():
    'Build git in previously unpacked git.srcdir().'
    log.info('building git')

    fs.goto(srcdir())

    from command import cmd,make

    if not os.path.exists('config.status'):
        log.info('configuring git')
        cmd('./configure --prefix=%s'%prefix())

    if os.path.exists('git'):
        log.info('git appears to already have been built')
    else:
        make()

    exe = gitexe()
    if os.path.exists(exe):
        log.info('git appears to already have been installed to',exe)
    else:
        make('install')
    return exe

def gitcmd(cmdstr):
    return cmd('%s %s'%(gitexe(),cmdstr),output=True)

def clone(url,target):
    ret = []
    ret.append(gitcmd('clone %s %s'%(url,target)))
    return '\n'.join(ret)

def fetch():
    return gitcmd('fetch')

def checkout(src,dst=None):
    if dst:
        return gitcmd('checkout -t -b %s %s'%(dst,src))
    else:
        return gitcmd('checkout %s'%src)

def pull():
    return gitcmd('pull')

def branch():
    return gitcmd('branch')

def submodule(rest):
    return gitcmd('submodule %s'%rest)

def branches():
    lbranches = []
    rbranches = []
    branches = gitcmd('branch -a').split('\n')

    for branch in branches:
        branch = branch.strip()
        if not branch: continue
        if branch[0] == '*': branch = branch[2:]
        if '/' in branch:
            rbranches.append(branch)
        else:
            lbranches.append(branch)
        continue

    return (lbranches,rbranches)

