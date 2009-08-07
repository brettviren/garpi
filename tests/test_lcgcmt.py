#!/usr/bin/env python

'''
Test the lcgcmt module
'''

lcgcmt = None


def test_make():
    global lcgcmt
    from garpi.lcgcmt import Lcgcmt
    lcgcmt = Lcgcmt()

def test_get():
    'Get the lcgcmt project'
    lcgcmt.download()
    from garpi import fs
    import os
    assert os.path.exists(fs.projects()+'/lcgcmt/cmt/project.cmt')

def test_update():
    test_get()
    
def test_setup():
    'Add setup scripts'

def test_env():
    env = lcgcmt.env()

def test_reachable_packages():
    from garpi import cmt
    pkgs = cmt.reachable_packages('LCG_Release',extra_env=lcgcmt.env(),
                                  dir=lcgcmt.proj_dir())
    assert pkgs['LCG_Release'] == lcgcmt.proj_dir(), 'LCG_Release not in consistent location: "%s" != "%s"'%(pkgs['LCG_Release'],lcgcmt.proj_dir())


def test_uses():
    from garpi import cmt
    uses = cmt.get_uses(lcgcmt.proj_dir() + '/LCG_Release')
    for use in uses:
        print str(use)
    
def test_cmtconfig():
    cfg = lcgcmt.cmtconfig()
    print cfg
    
if '__main__' == __name__:
    test_make()
    # test_get()
    # test_update()
    # test_setup()
    # test_env()
    # test_reachable_packages()
    # test_uses()
    test_cmtconfig()
