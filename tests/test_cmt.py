#!/usr/bin/env python
'''
Test the cmt module
'''

from garpi import cmt, fs
import os

def test_download():
    tgz = cmt.download()
    assert os.path.exists(tgz),'No cmt tar file: '+tgz

def test_unpack():
    srcdir = cmt.unpack()
    assert os.path.exists(srcdir),'No src directory: '+srcdir

def test_build():
    cmtexe = cmt.build()
    assert os.path.exists(cmtexe),'No cmt executable: '+cmtexe

def test_setup():
    setup = cmt.setup()
    assert os.path.exists(setup),'No setup file: '+setup


def test_help():
    'Test basic running of cmt'
    msg = cmt.cmt('--help' , output=True)
    msg = msg.split('\n')
    line1 = msg[0].strip()
    assert line1 == '#> cmt command [option...]','Unknown response from cmt: "%s"'%line1

def test_show():
    'Test the various "cmt show" functions'
    mac = cmt.macros()
    assert mac['CMTROOT'] == cmt.srcdir(), 'Got inconsistent src dirs "%s" != "%s"'%(mac['CMTROOT'],cmt.srcdir())
    sets = cmt.sets()
    assert sets.has_key('NEWCMTCONFIG')
    tags = cmt.tags()
    assert tags.has_key('Unix')  # Ha!

def test_uses():
    pkgdir='projects/interim/InterimRelease'
    uses = cmt.get_uses(pkgdir)
    print 'Got %d uses:'%len(uses)
    for use in uses:
        print 'Use:',use,'use.project=',use.project

if '__main__' == __name__:
    #test_download()
    #test_unpack()
    #test_build()
    #test_setup()
    #test_help()
    #test_show()
    test_uses()
