#!/usr/bin/env python

import os,shutil

from garpi.get import get, uriparse

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

def test_uriparse():
    urls = [
        'http://www.phy.bnl.gov/~bviren/garpi/releases/lcgcmt-20101014.tar.gz',
        'cvs+pserver://anonymous@lcgcmt.cvs.cern.ch/cvs/LCGCMT/lcgcmt',
        ]
    for url in urls:
        urlp = uriparse(url)
        print url,urlp
        if 'cvs' in urlp[0]:
            scheme = urlp[0].split("+")
            print 'CVS URL :%s:%s:%s'%(scheme[1],urlp[1],'/'.join(urlp[2].split('/')[:-1]))    


if '__main__' == __name__:
    #test_get_git()
    test_uriparse()
    
