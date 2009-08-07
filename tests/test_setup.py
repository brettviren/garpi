#!/usr/bin/env python

import garpi.setup,garpi.fs,garpi.util,garpi.command
import os

def test_create():
    'Create top level configuration'
    garpi.setup.init()

    base = garpi.fs.setup()
    assert os.path.exists(base),'Directory not created: '+base
    for ext in ['.sh','.csh']:
        file = base+ext
        assert os.path.exists(file),'Setup script created: '+file

if '__main__' == __name__:
    test_create()

