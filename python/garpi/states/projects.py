'''
States handling projects
'''

class Project:
    def __init__(self,name):
        self.name = name
        self.NAME = name.upper()
        return

    def register(self,garpi):
        self.garpi = garpi
        garpi.machine.add_state('%s_START'%self.NAME,self.start)
        garpi.machine.add_state('%s_DOWNLOAD'%self.NAME,self.download)
        garpi.machine.add_state('%s_CONFIG'%self.NAME,self.config)
        garpi.machine.add_state('%s_BUILD'%self.NAME,self.build)
        return
    
    def start(self,cargo):
        return ('%s_DOWNLOAD'%self.NAME,cargo)
    
    def download(self,cargo):
        log.info(self.name +' download')
        projdir = self.garpi.go.projects()
        url = self.garpi.cfg.get(self.name,self.name + '_url')
        from get import get
        get(url,projdir,True)
        return ('%s_CONFIG'%self.NAME,cargo)
        
    def config(self,cargo):
        release_package = self.garpi.cfg.get(self.name,self.name + '_release_package')
        if release_package is None or release_package == 'None':
            return ('%s_BUILD'%self.NAME,cargo)
        projdir = self.garpi.go.projects()
        

            
        
