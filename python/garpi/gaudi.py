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
        # Gaudi has a peculiar repository
        if url[:3] == 'git': return self._download_git()
        if url[:3] == 'svn' and 'cern.ch' in url: self._download_cern_svn()
        return Project.download(self)

    def _download_cern_svn(self):
        import fs
        from svn import svncmd
        scheme = self.url().split('+')

        if self.tag() == 'trunk':
            url = '%s/trunk'%scheme[1]
        else:
            url = '%s/tags/GAUDI/GAUDI_%s'%(scheme[1],self.tag())
        svncmd('co %s %s/gaudi'%(url,fs.projects()))
        return

            

    def _download_git(self):
        url = self.url()
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

        fs.goto(fs.projects(),True)
        git.clone(url,'gaudi')
        fs.goback()

        fs.goto(os.path.join(fs.projects(),'gaudi'),True)
        git.submodule('init')
        git.submodule('update')
        fs.goback()

        return

    def checkout(self,pkg,tag):
        import fs,git
        fs.goto(os.path.join(fs.projects(),'gaudi',pkg))

        lbranches,rbranches = git.branches()
        if tag in lbranches:
            git.checkout(tag)
        else:
            git.checkout('origin/'+tag,tag)

        fs.goback()
        return

