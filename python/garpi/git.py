#!/usr/bin/env python

'''
Thin functional wrapper over the git programs
'''

from command import cmd

def clone(url,target):
    return cmd('git clone %s %s'%(url,target),output=True)

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
