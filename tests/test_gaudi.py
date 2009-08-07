#!/usr/bin/env python
'Test the garpi.gaudi module'

def test_get_gaudi():
    'Download the gaudi project.'
    from garpi.gaudi import Gaudi
    gaudi = Gaudi()
    gaudi.download()

def test_externals():
    'Test finding the externals'
    from garpi.gaudi import Gaudi
    gaudi = Gaudi()
    exclusions = ['GaudiPoolDb','GaudiGridSvc',
                  'HbookCnv','RootHistCnv']
    externs = gaudi.externals(exclusions)
    for name,use in externs.iteritems():
        print str(use)
        assert name not in exclusions, name+' was supposed to be excluded'
        #assert use.project == 'lcgcmt', 'LCG_Interface package from Unkown project: '+use.project
        #assert use.directory == 'LCG_Interfaces', 'Unknown directory: '+use.directory

if '__main__' == __name__:
    #test_get_gaudi()
    test_externals()
