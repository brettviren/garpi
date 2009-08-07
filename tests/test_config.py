#!/usr/bin/env python

def fake_argv():
    'Force argv to be some value for testing into /tmp'
    import sys
    old_argv = sys.argv
    sys.argv = ['/usr/bin/python',
                '-n','test-release',
                '-b','/tmp/test-install',
                '-l','test.log']
    from garpi.config import cli
    sys.argv = old_argv
    return cli

def test_import():
    'Do command some line options and config parsing'

    # save away real argv. Only needed to override real command line
    cli = fake_argv()
    assert cli.opts.base_directory == '/tmp/test-install'
    assert cli.opts.name == 'test-release'
    assert cli.file.get('cmt','cmt_site_url') == 'http://www.cmtsite.org'



if '__main__' == __name__:
    test_import()
