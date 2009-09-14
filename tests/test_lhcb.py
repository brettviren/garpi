#!/usr/bin/env python
'Test the garpi.projects module to build lhcb'


lhcb = None


def test_make_lhcb_object():
    from garpi.projects import Project
    global lhcb
    lhcb = Project("lhcb")

def test_get_lhcb():
    'Download the lhcb project.'
    lhcb.download()

externs = []

def test_list_externals():
    'Test finding the externals'
    exclusions = []
    global externs
    externs = lhcb.externals(exclusions=exclusions)
    assert externs, 'Got no externals for lhcb'

    from garpi.lcgcmt import Lcgcmt
    lcgcmt = Lcgcmt()

    externs = lcgcmt.builder_externals(externs,exclusions=exclusions)
    assert externs, 'Got no externals for lhcb'
    for pkg in externs:
        print pkg
        assert pkg not in exclusions, pkg+' was supposed to be excluded'

def test_build_externals():
    'Build the externs found in the previous test'
    from garpi.lcgcmt import Lcgcmt
    lcgcmt = Lcgcmt()
    for pkg in externs:
        lcgcmt.build_package(pkg)

def test_config_lhcb():
    'Configure the lhcb project'
    lhcb.broadcast('cmt config')

def test_build_lhcb():
    'Build the lhcb project'
    lhcb.broadcast('make')


if '__main__' == __name__:
    test_make_lhcb_object()
    #test_get_lhcb()
    #test_list_externals()
    #test_build_externals()
    #test_config_lhcb()
    test_build_lhcb()
