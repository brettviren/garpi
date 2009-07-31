'''
States handling projects
'''

from util import log, cmd, source2env

class Project:
    def __init__(self,garpi,name):
        self.garpi = garpi
        self.name = name
        self.NAME = name.upper()
        return

    def url(self):
        return self.garpi.cfg.get('project_'+self.name,self.name + '_url')

    def tag(self):
        return self.garpi.cfg.get('project_'+self.name,self.name + '_tag')

    def rel_pkg(self):
        'Return the path to the release package from top of project or None'
        rp = self.garpi.cfg.get(self.name,self.name + '_release_package')
        if rp.lower == 'none': rp = None
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
        if relpkg is None: return env1
        self.garpi.go.to(relpkg + '/cmt')
        if not os.path.exists('setup.sh'):
            cmd('cmt config',env1)
        env2 = source2env('setup.sh')
        env1.update(env2)
        return env1

    def config(self):
        '''Configure all packages reached by the project's release package'''
        env = self.env()
        cmd('cmt br cmt config',env)
        return

            
        
