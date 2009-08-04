'''
States handling projects
'''

from util import log, cmd, source2env
from exception import CommandFailure
import os

class Project:
    def __init__(self,garpi,name):
        self.garpi = garpi
        self.name = name
        self.NAME = name.upper()
        return

    def get_config(self,what):
        'Get the PROJECT_WHAT config from the project_PROJECT section'
        return self.garpi.cfg.get('project_'+self.name,self.name + '_' + what)

    def url(self): return self.get_config('url')
    def tag(self): return self.get_config('tag')
    def rel_pkg(self):
        'Return the path to the release package from top of project or None'
        rp = self.get_config('release_package')
        if rp.lower() == 'none': rp = ''
        return rp

    def download(self):
        '''Download missing or update pre-existing project files.  As
        a side effect the program will be in the projects directory
        that contains the downloaded project'''
        log.info(self.name +' download')
        projdir = self.garpi.go.projects()
        from get import get
        get(self.url(),self.name,True,tag=self.tag())
        return
        
    def env(self):
        '''Return dictionary of env for the given project.  It conists
        of the environment after sourcing the top level
        projects/setup.sh followed by the setup.sh in the release
        package.  As a side effect, the program is left in the project
        relaease package's cmt sub directory.'''
        projdir = self.garpi.go.projects()
        env1 = source2env('setup.sh')
        relpkg = self.rel_pkg()
        if not relpkg: return env1
        self.garpi.go.to(relpkg + '/cmt')
        if not os.path.exists('setup.sh'):
            cmd('cmt config',env1)
        env2 = source2env('setup.sh')
        env1.update(env2)
        return env1

    def cmd_inrel(self,cmdstr):
        'Run a command in the release package.  No-op if none defined.'
        relpkg = self.rel_pkg()
        if not relpkg: 
            err = 'Project %s has no release package defined'%self.name
            log.warning(err)
            raise CommandFailure,err
        relpkgcmt = self.garpi.dir.projects()+'/'+relpkg+'/cmt'
        if not os.path.exists(relpkgcmt):
            err = 'Project %s has release package defined, but no dir: %s'%(self.name,relpkgcmt)
            log.warning(err)
            raise CommandFailure,err
        cmd(cmdstr,self.env())

    def config(self):
        '''Configure all packages reached by the project's release package'''
        self.cmd_inrel('cmt br cmt config')
        return

    def make(self,target=""):
        '''Broadcast a make from the projects release pacakge'''
        self.cmd_inrel('cmt br make %s'%target)

        
        
