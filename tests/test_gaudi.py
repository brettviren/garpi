#!/usr/bin/env python
'Test the garpi.gaudi module'

def test_get_gaudi():
    'Download the gaudi project.'
    from garpi.gaudi import Gaudi
    gaudi = Gaudi()
    gaudi.download()


if '__main__' == __name__:
    test_get_gaudi()
