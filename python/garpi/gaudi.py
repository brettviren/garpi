#!/usr/bin/env python

from projects import Project
from util import log
import os

class Gaudi(Project):
    def __init__(self):
        Project.__init__(self,"gaudi")
        return

    def download(self):
        url = self.url()
        if url[:3] != 'git': return Project.download(self)
        if url[4] == '+': url = url[4:]
        log.info(self.name +' download')

        # Get super project
        self.clone(url)

        # Get release package
        self.checkout(self.rel_pkg(),self.tag())
        
        self.init_project(['lcgcmt'])

        # Get versions
        import cmt
        uses = cmt.get_uses(self.proj_dir()+'/'+self.rel_pkg())
        for use in uses:
            #print 'use:',use.name,use.project,use.directory,use.version
            if use.project == 'gaudi' and use.directory == '':
                if '*' in use.version:
                    log.info('Skipping %s %s'%(use.name,use.version))
                    continue
                self.checkout(use.name,use.version)

    def clone(self,url):
        import fs,git
        target = fs.projects()+'/gaudi'
        if os.path.exists(target):
            log.info('Directory already exists, skipping clone to: %s'%target)
            return

        fs.goto(fs.projects())
        git.clone(url,'gaudi')
        fs.goback()

        fs.goto(fs.projects()+'/gaudi')
        git.submodule('init')
        git.submodule('update')
        fs.goback()

        return

    def checkout(self,pkg,tag):
        import fs,git
        fs.goto(fs.projects()+'/gaudi/'+pkg)

        lbranches,rbranches = git.branches()
        if tag in lbranches:
            git.checkout(tag)
        else:
            git.checkout('origin/'+tag,tag)

        fs.goback()
        return

