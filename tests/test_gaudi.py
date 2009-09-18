#!/usr/bin/env python
'Test the garpi.gaudi module'


gaudi = None


def test_make_gaudi_object():
    from garpi.gaudi import Gaudi
    global gaudi
    gaudi = Gaudi()

def test_get_gaudi():
    'Download the gaudi project.'
    gaudi.download()

externs = []

def test_list_externals():
    'Test finding the externals'
    exclusions = ['GaudiPoolDb','GaudiGridSvc',
                  'HbookCnv','RootHistCnv','PCRE']
    exclusions = []
    global externs
    externs = gaudi.externals(exclusions=exclusions)
    assert externs, 'Got no externals for gaudi'

    from garpi.lcgcmt import Lcgcmt
    lcgcmt = Lcgcmt()

    externs = lcgcmt.builder_externals(externs,exclusions=exclusions)
    assert externs, 'Got no externals for gaudi'
    for pkg in externs:
        print pkg
        assert pkg not in exclusions, pkg+' was supposed to be excluded'

def test_build_externals():
    'Build the externs found in the previous test'
    from garpi.lcgcmt import Lcgcmt
    lcgcmt = Lcgcmt()
    for pkg in externs:
        lcgcmt.build_package(pkg)

def test_config_gaudi():
    'Configure the gaudi project'
    gaudi.broadcast('cmt config')

def test_build_gaudi():
    'Build the gaudi project'
    gaudi.broadcast('make')


if '__main__' == __name__:
    test_make_gaudi_object()
    #test_get_gaudi()
    test_list_externals()
    #test_build_externals()
    #test_config_gaudi()
    #test_build_gaudi()
