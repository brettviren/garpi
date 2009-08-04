#!/usr/bin/env python

import os
from garpi.exception import CommandFailure

def test_project():
    from garpi.projects import Project
    from garpi.main import Garpi  
    base = os.path.dirname(__file__)
    base = os.path.dirname(base)
    if base != "": base = base + '/'
    base = base + 'test-install'
    print 'base =',base
    g = Garpi(['-n','test-release','-b',base])
    p = Project(g,'lcgcmt')
    p.download()
    try:
        p.config()
        p.make()
    except CommandFailure,err:
        pass

if '__main__' == __name__:
    test_project()
