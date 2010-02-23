#!/usr/bin/env python
'''
Simple wrapper around CVS executable
'''
from command import cmd
import os, fs

def cvsexe(): return 'cvs'

def cvscmd(cmdstr):
    return cmd('%s %s'%(cvsexe(),cmdstr),output=True)

