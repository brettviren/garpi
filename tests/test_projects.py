#!/usr/bin/env python

from garpi import projects 

def test_env():
    'Test project environ'
    p = projects.Project('lcgcmt')
    env = p.cfg_environ()
    for k,v in env.iteritems():
        print k,v

if __name__ == '__main__':
    test_env()
