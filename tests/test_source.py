#!/usr/bin/env python

from garpi.command import source
from garpi import fs
import os

def test_builder():
    print 'Source %s/setup.sh'%fs.projects()
    env1 = source('./setup.sh',dir=fs.projects())

    for k,v in env1.items():
        if k[:2] == 'G4' or k == 'SITEROOT':
            print 'env1 %s=%s'%(k,v)

    cmtdir = os.path.join(fs.projects(),'lcgcmt/LCG_Builders/wcsim/cmt')

    print 'Source %s/setup.sh'%cmtdir
    env2 = source('./setup.sh',env=env1,dir=cmtdir)

    for k,v in env2.items():
        if k[:2] == 'G4' or k == 'SITEROOT':
            print 'env2 %s=%s'%(k,v)

    
if '__main__' == __name__:
    test_builder()
