#!/usr/bin/env python
'Test the garpi.gaudi module'

def test_get_gaudi():
    'Download the gaudi project.'
    from garpi.gaudi import Gaudi
    gaudi = Gaudi()
    gaudi.download()

def test_list_externals():
    'Test finding the externals'
    from garpi.gaudi import Gaudi
    gaudi = Gaudi()
    exclusions = ['GaudiPoolDb','GaudiGridSvc',
                  'HbookCnv','RootHistCnv','PCRE']
    externs = gaudi.externals(exclusions=exclusions)
    assert externs, 'Got no externals for gaudi'
    for pkg in externs:
        print pkg
        assert pkg not in exclusions, pkg+' was supposed to be excluded'

def test_build_externals():
    return

if '__main__' == __name__:
    #test_get_gaudi()
    test_list_externals()
    test_build_externals()
