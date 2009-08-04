#!/usr/bin/env python

'''
Wrapper for CMT installation and use
'''

from util import untar
from config import cli
import fs

def ver(self):
    return cli.file.get('cmt','cmt_version')

def tgz(self):
    return "CMT%s.tar.gz"%self.ver()

def base_url(self):
    return cli.file.get('cmt','cmt_site_url')

def url(self):
    return '%s/%s/%s'%(self.base_url(),self.ver(),self.tgz())

def srcdir(self):
    return fs.external() + '/CMT/'+self.ver()

def download(self,cargo):
    log.info('downloading cmt tar file')
    target = "%s/%s"%(fs.external(),self.tgz())
    from get import get
    get(self.url(),target)
    if not os.path.exists(self.tgz()):
        raise InconsistentState,'Tar file does not exist: %s%s'%(os.getcwd(),self.tgz())
        return

def unpack(self,cargo):
    log.info('unpacking cmt source')
    target = self.srcdir()
    if os.path.exists(target):
        log.info('CMT appears to already be unpacked in %s'%(target))
        return ('CMT_BUILD',cargo)
    fs.goto(fs.external())
    untar(self.tgz())
    return

def build(self,cargo):
    log.info('building cmt')
    target = self.srcdir() + '/mgr/setup.sh'
    if os.path.exists(target):
        err = 'CMT appears to already have be initialized, found: %s'%target
        log.info(err)        
        return
    fs.goto(self.srcdir() + '/mgr/')
    cmd('./INSTALL')
    env = source2env('setup.sh')
    cmt = '%s/%s/cmt'%(self.srcdir(),env['CMTCONFIG'])
    if os.path.exists(cmt):
        log.info('CMT appears to already have been built: %s'%cmt)
    else:
        cmd('make',env=env)
    return

def setup(self,cargo):
    setup = self.srcdir() + '/mgr/setup'
    setupdir = self.garpi.go.setup()
    def do_link(ext):
        if os.path.exists('00_cmt'+ext): return
        os.symlink(setup+ext,'00_cmt'+ext)
    for ext in ['.sh','.csh']:
        do_link(ext)
    return
        
