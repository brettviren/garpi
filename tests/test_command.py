#!/usr/bin/env python

import os

def test_source():
    'Test sourcing a setup script to retrieve new env and any output'

    test_value1="hello world"
    test_value2="value set = in test_source.sh"
    filename = os.path.dirname(__file__) + '/test_source.sh'
    fp = open(filename,"w")
    fp.write('''
TEST_SETUP1="%s"
TEST_SETUP2="%s"
export TEST_SETUP1 TEST_SETUP2
echo "setting TEST_SETUP1 to \\"$TEST_SETUP1\\""
echo "setting TEST_SETUP2 to \\"$TEST_SETUP2\\""
'''%(test_value1,test_value2))
    fp.close()

    from garpi.command import source
    (env,out) = source(filename,output=True)
    #print env
    #print out
    for a,b in [('TEST_SETUP1',test_value1),('TEST_SETUP2',test_value2)]:
        val = env[a]
        assert val == b, 'Got wrong value: "%s" != "%s"'%(val,b)
    output='''setting TEST_SETUP1 to "hello world"
setting TEST_SETUP2 to "value set = in test_source.sh"'''
    assert out==output, 'Output of source not matched:"%s" != "%s"'%(out,output)

if '__main__' == __name__:
    test_source()

