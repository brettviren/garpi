#!/usr/bin/env python

import os,shutil

from garpi.get import get

def test_get_git():
    url = "git+ssh://lycastus.phy.bnl.gov/home/bviren/work/garpi/projects/garpi-lcgcmt"
    tag = "LCGCMT_56c"
    
    target = os.path.dirname(__file__)
    target += '/test_get'
    if os.path.exists(target):
        shutil.rmtree(target)
    get(url,target,tag=tag)

    for thing in ['.git','cmt/project.cmt']:
        test = target + '/' + thing
        assert os.path.exists(test),'Could not find: '+test

if '__main__' == __name__:
    test_get_git()
