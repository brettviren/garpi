'''
States for installing CMT
'''
from garpi.util import log, untar, source2env, cmd
from garpi.exception import InconsistentState
import os

class CmtStates:
    def __init__(self):
        return

    def register(self,garpi):
        self.garpi = garpi
        garpi.machine.add_state('CMT_START',self.start)
        garpi.machine.add_state('CMT_DOWNLOAD',self.download)
        garpi.machine.add_state('CMT_UNPACK',self.unpack)
        garpi.machine.add_state('CMT_BUILD',self.build)
        garpi.machine.add_state('CMT_SETUP',self.setup)
        return

    def ver(self):
        return self.garpi.cfg.get('cmt','cmt_version')

    def tgz(self):
        return "CMT%s.tar.gz"%self.ver()

    def base_url(self):
        return self.garpi.cfg.get('cmt','cmt_site_url')

    def url(self):
        return '%s/%s/%s'%(self.base_url(),self.ver(),self.tgz())

    def srcdir(self):
        return self.garpi.dir.external() + '/CMT/'+self.ver()

    def start(self,cargo):
        return ('CMT_DOWNLOAD',cargo)

    def download(self,cargo):
        log.info('cmt download')

        target = "%s/%s"%(self.garpi.go.external(),self.tgz())
        from get import get
        get(self.url(),target)
        self.check_tgz()
        return ('CMT_UNPACK',cargo)

    def check_tgz(self):
        if not os.path.exists(self.tgz()):
            raise InconsistentState,'Tar file does not exist: %s%s'%(os.getcwd(),self.tgz())
        return

    def unpack(self,cargo):
        log.info('cmt unpack')
        target = self.srcdir()
        if os.path.exists(target):
            log.info('CMT appears to already be unpacked in %s'%(target))
            return ('CMT_BUILD',cargo)
        self.garpi.go.external()
        self.check_tgz()
        untar(self.tgz())
        return ('CMT_BUILD',cargo)

    def build(self,cargo):
        log.info('cmt build')
        target = self.srcdir() + '/mgr/setup.sh'
        self.garpi.go.to(self.srcdir() + '/mgr/')
        if os.path.exists(target):
            log.info('CMT appears to already have be initialized, found: %s'%target)
        else:
            cmd('./INSTALL')

        env = source2env('setup.sh')
        cmt = '%s/%s/cmt'%(self.srcdir(),env['CMTCONFIG'])
        if os.path.exists(cmt):
            log.info('CMT appears to already have been built: %s'%cmt)
        else:
            cmd('make',env=env)
        return ('CMT_SETUP',cargo)

    def setup(self,cargo):
        setup = self.srcdir() + '/mgr/setup'
        setupdir = self.garpi.go.setup()
        def do_link(ext):
            if os.path.exists('00_cmt'+ext): return
            os.symlink(setup+ext,'00_cmt'+ext)
        for ext in ['.sh','.csh']:
            do_link(ext)
        return ('CMT_DONE',cargo)        
        
