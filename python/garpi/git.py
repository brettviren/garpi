#!/usr/bin/env python

'''
Thin functional wrapper over the git programs
'''

from command import cmd
import os

def clone(url,target):
    ret = []
    ret.append(cmd('git clone %s %s'%(url,target),output=True))
    return '\n'.join(ret)

def fetch():
    return cmd('git fetch',output=True)

def checkout(src,dst=None):
    if dst:
        return cmd('git checkout -t -b %s %s'%(dst,src),output=True)
    else:
        return cmd('git checkout %s'%src,output=True)

def pull():
    return cmd('git pull',output=True)

def branch():
    return cmd('git branch',output=True)

def submodule(rest):
    return cmd('git submodule %s'%rest,output=True)

def branches():
    lbranches = []
    rbranches = []
    branches = cmd('git branch -a',output=True).split('\n')

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

