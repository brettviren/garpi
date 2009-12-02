#!/usr/bin/env python
'''
Simple wrapper around svn executable
'''
from command import cmd
import os, fs

def svnexe(): return 'svn'

def svncmd(cmdstr):
    return cmd('%s %s'%(svnexe(),cmdstr),output=True)

