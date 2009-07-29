def test_source2env():
    test_value="value set = in test_misc.py.sh"
    filename = __file__ + '.sh'
    fp = open(filename,"w")
    fp.write('''
TEST_MISC="%s"
export TEST_MISC
'''%test_value)
    fp.close()

    from garpi.util import source2env
    env = source2env(filename)
    myval = env['TEST_MISC']
    assert myval == test_value, 'Got wrong value: "%s" != "%s"'%(myval,test_value)
    #print env

if '__main__' == __name__:
    test_source2env()
