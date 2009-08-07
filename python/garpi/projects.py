'''
States handling projects
'''

from util import log
from exception import CommandFailure
import os

class Project:
    def __init__(self,name):
        self.name = name
        self.NAME = name.upper()
        return

    def get_config(self,what):
        'Get the PROJECT_WHAT config from the project_PROJECT section'
        from config import cli
        return cli.file.get('project_'+self.name,self.name + '_' + what)

    def proj_dir(self):
        import fs
        return os.path.join(fs.projects(), self.name)

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
        import fs
        projdir = fs.projects()
        fs.goto(projdir)
        from get import get
        get(self.url(),self.name,True,tag=self.tag())
        fs.goback
        return
        
    def env(self):
        '''Return dictionary of env for the given project.  It conists
        of the environment after sourcing the top level
        projects/setup.sh followed by the setup.sh in the release
        package.  As a side effect, the program is left in the project
        relaease package's cmt sub directory.'''
        from command import source
        import fs
        env1 = source('./setup.sh',dir=fs.projects())
        relpkg = self.rel_pkg()
        if not relpkg: 
            return env1
        cmtdir = os.path.join(self.proj_dir(),relpkg,'/cmt')
        import cmt
        if not os.path.exists(cmtdir+'/setup.sh'):
            cmt.cmt('config',extra_env=env1,dir=cmtdir)
            pass
        env2 = source('./setup.sh',dir=cmtdir)
        env1.update(env2)
        return env1

    def cmd_inrel(self,cmdstr):
        'Run a command in the release package.  No-op if none defined.'
        relpkg = self.rel_pkg()
        if not relpkg: 
            err = 'Project %s has no release package defined'%self.name
            log.warning(err)
            raise CommandFailure,err
        relpkgcmt = os.path.join(self.garpi.dir.projects(),relpkg,'/cmt')
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

        
    def init_project(self,deps=[]):
        import fs
        fs.assure(self.proj_dir()+'/cmt')
        fp = open(self.proj_dir()+'/cmt/project.cmt','w')
        fp.write('project %s\n'%self.name)
        for dep in deps: fp.write('use %s\n'%dep)
        fp.write('''
build_strategy with_installarea
structure_strategy with_no_version_directory
setup_strategy root\n''')
        fp.write('container %s'%self.rel_pkg())
        fp.close()
        return

    def externals(self,exclusions = []):
        '''
        Start in the release package, find all the uses that are under
        LCG_Interface, and thus external.  Any package in the
        exclusions list and its dependencies will be excluded from the
        results.  Result dictionary mapping a package name to a
        cmt.UsedPackage object.
        '''
        import cmt
        uses = cmt.get_uses(os.path.join(self.proj_dir(),self.rel_pkg()))
        reduced = {}
        # Convert to name keyed dict
        for use in uses:
            #if use.project != 'lcgcmt': continue
            #if use.directory != 'LCG_Interfaces': continue
            reduced[use.name] = use
            continue
        # Trim top level uses
        for kill in exclusions:
            if reduced.has_key(kill):
                del reduced[kill]
            continue
        # Trim dependencies
        ret = {}
        for name,used in reduced.iteritems():
            newuses=[]
            for dep in used.uses:
                #if dep.project != 'lcgcmt': continue
                #if dep.directory != 'LCG_Interfaces': continue
                if dep.name not in exclusions: newuses.append(dep)
            used.uses = newuses
            ret[name] = used
        return reduced
        
                            
