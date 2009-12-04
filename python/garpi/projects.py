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

    def tags(self):
        import cmt
        rel_path = os.path.join(self.proj_dir(),self.rel_pkg(),'cmt')
        extra_env = cmt.env(rel_path)
        return cmt.tags(extra_env=extra_env,dir=rel_path)

    def sets(self):
        import cmt
        rel_path = os.path.join(self.proj_dir(),self.rel_pkg(),'cmt')
        extra_env = cmt.env(rel_path)
        return cmt.sets(extra_env=extra_env,dir=rel_path)

    def macro(self,name):
        import cmt
        rel_path = os.path.join(self.proj_dir(),self.rel_pkg(),'cmt')
        extra_env = cmt.env(rel_path)
        return cmt.macro(name,extra_env=extra_env,dir=rel_path).strip()



    def get_config(self,what):
        'Get the WHAT config from the project_PROJECT section'
        from config import cli
        return cli.file.get('project_'+self.name,what)

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
        fs.goto(projdir,True)
        from get import get
        get(self.url(),self.name,True,tag=self.tag())
        fs.goback
        return
        
    def env(self,rel_dir=None):
        '''Return dictionary of env for the given project.  It conists
        of the environment after sourcing the top level
        projects/setup.sh followed by the setup.sh in the release
        package.'''
        from command import source
        import fs
        env1 = source('./setup.sh',dir=fs.projects())
        if not rel_dir: rel_dir = self.rel_pkg()
        if not rel_dir: return env1
        cmtdir = os.path.join(self.proj_dir(),rel_dir,'cmt')
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
        import fs
        relpkgcmt = os.path.join(fs.projects(),self.name,relpkg,'cmt')
        if not os.path.exists(relpkgcmt):
            err = 'Project %s has release package defined, but no dir: %s'%(self.name,relpkgcmt)
            log.warning(err)
            raise CommandFailure,err
        import command
        command.cmd(cmdstr,env=self.env(),dir=relpkgcmt)

    def config(self):
        '''Configure all packages reached by the project's release package'''
        self.cmd_inrel('cmt br cmt config')
        return

    def broadcast(self,what):
        'Broadcast a command from the release package'
        self.cmd_inrel('cmt br %s'%what)

    def make(self,target=""):
        'Broadcast a make from the projects release pacakge'
        self.broadcast('make %s'%target)

        
    def init_project(self,deps=None):
        if deps is None: deps = list()
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

    def externals(self,package = None, exclusions = None):
        '''
        Start in the given package else use this project's release
        package, find all the uses that are under LCG_Interface, and
        thus external.  Any package in the exclusions list and its
        dependencies will be excluded from the results.  Return
        ordered list of the package name.
        '''
        if exclusions is None: exclusions = list()

        if not package:
            package = self.rel_pkg()
        pkg_dir = os.path.join(self.proj_dir(),package)

        import cmt
        uses = cmt.get_uses(pkg_dir)

        #print 'Checking for uses in "%s"'%pkg_dir

        # Categorize the packages as being directly used or a
        # potential extern
        myuses = []
        mynames = []
        for use in uses:
            #print 'USE:',use,'project:',use.project
            if not use.project == self.name: continue
            if use.name in exclusions:
                log.info('Excluding "%s"'%use.name)
                continue
            if use.name in mynames: 
                continue
            log.info('Including "%s"'%use.name)
            myuses.append(use)
            mynames.append(use.name)
            continue
        
        def deps(use,names):
            for dep in use.uses:
                #print '"%s" uses "%s" [%s]'%(use.name,dep.name,str(dep))
                if dep.project != 'lcgcmt' \
                        or dep.directory != 'LCG_Interfaces':
                    continue
                if dep.name in exclusions:
                    log.warn('Skipping excluded pkg "%s" needed by "%s"'%(dep.name,use.name))
                    continue
                deps(dep,names)
                if dep.name not in names:
                    names.append(dep.name)
                    log.info('Adding "%s" needed by "%s"'%(dep.name,use.name))
                continue
            if use.project == 'lcgcmt' \
                    and use.directory == 'LCG_Interfaces' \
                    and use.name not in names:
                names.append(use.name)

            return

        names = []
        for use in myuses:
            deps(use,names)
        return names
        
                            
