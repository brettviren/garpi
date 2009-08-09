#!/usr/bin/env python

'''
Test the lcgcmt module
'''

lcgcmt = None

import os

def test_make():
    global lcgcmt
    from garpi.lcgcmt import Lcgcmt
    lcgcmt = Lcgcmt()

def test_get():
    'Get the lcgcmt project'
    lcgcmt.download()
    from garpi import fs
    assert os.path.exists(fs.projects()+'/lcgcmt/cmt/project.cmt')

def test_update():
    test_get()
    
def test_init():
    'Add setup scripts'
    lcgcmt.init_project()

def test_env():
    env = lcgcmt.env()

def test_reachable_packages():
    from garpi import cmt
    pkgs = cmt.reachable_packages('LCG_Release',extra_env=lcgcmt.env(),
                                  dir=lcgcmt.proj_dir())
    assert pkgs['LCG_Release'] == lcgcmt.proj_dir(), 'LCG_Release not in consistent location: "%s" != "%s"'%(pkgs['LCG_Release'],lcgcmt.proj_dir())


def test_uses():
    from garpi import cmt
    dir = os.path.join(lcgcmt.proj_dir(),'LCG_Release')
    #print 'Getting uses from %s'%dir
    uses = cmt.get_uses(dir)
    for use in uses:
        print str(use)
    
def test_cmtconfig():
    cfg = lcgcmt.cmtconfig()
    print cfg
    
pkgs = [
    "Python",
    "GCCXML",
    "ROOT",
    "Reflex",
    "Boost",
    "CppUnit",
    "CLHEP",
    "AIDA",
    "uuid",
    "XercesC",
    "GSL",
    "HepPDT",
    ]

def test_builder_finder():
    for pkg in pkgs:
        builddir = lcgcmt.builder_directory(pkg)
        if pkg == "Reflex":
            assert builddir is None, "Reflex shouldn't have a builder"
        else:
            assert builddir,'No build directory for "%s"'%pkg
        print '%s built by %s'%(pkg,builddir)

def test_build_packages():
    #lcgcmt.build_package('AIDA')
    lcgcmt.build_package('uuid')

if '__main__' == __name__:
    test_make()
    #test_get()
    #test_update()
    test_init()
    # test_env()
    # test_reachable_packages()
    # test_uses()
    test_cmtconfig()
    # test_builder_finder()
    test_build_packages()
