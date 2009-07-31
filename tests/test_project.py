#!/usr/bin/env python

import os

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
    p.config()

if '__main__' == __name__:
    test_project()
