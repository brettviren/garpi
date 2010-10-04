#!/usr/bin/env python

def test_directories():
    from garpi import fs
    print 'projects',fs.projects()
    print 'external',fs.external()

if '__main__' == __name__:
    test_directories()
