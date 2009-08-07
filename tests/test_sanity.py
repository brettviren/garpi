#!/usr/bin/env python
'''
Test the sanity module
'''

from garpi import sanity
def test_sanity():
    sanity.check()

if '__main__' == __name__:
    test_sanity()
