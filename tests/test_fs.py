#!/usr/bin/env python

def test_projects():
    from garpi import fs
    print fs.projects()

if '__main__' == __name__:
    test_projects()
