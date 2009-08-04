
from garpi.util import log


def test_setup():
    print 'importing setup'
    from garpi.util import log_maker
    print 'setting up'
    log_maker.set_file('test_log.log')
    print 'done'

def test_info():
    print 'calling info'
    log.info('test')
    print 'done'

if '__main__' == __name__:
    test_setup()
    test_info()
