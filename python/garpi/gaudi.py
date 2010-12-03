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
        print 'gaudi url: "%s"'%url
        print 'gaudi tag: "%s"'%self.tag()
        # Gaudi has a peculiar repository
        if url[:3] == 'git': return self._download_git_monolithic()
        if url[:3] == 'svn' and 'cern.ch' in url: self._download_cern_svn()
        return Project.download(self)

    def _download_cern_svn(self):
        import fs
        from svn import svncmd
        scheme = self.url().split('+')

        if self.tag() == 'trunk':
            url = '%s/trunk'%scheme[1]
        else:
            url = '%s/tags/GAUDI/%s'%(scheme[1],self.tag())
        # installing from a branch not supported/recommended.

        svncmd('co %s %s/gaudi'%(url,fs.projects()))
        return            


    def _download_git_monolithic(self):
        'If gaudi is served from a monolithic git repo'
        url = self.url()
        if url[4] == '+': url = url[4:]
        log.info(self.name +' download')

        # Get super project
        self._git_clone(url)

        # Get release package
        self._git_checkout(self.tag())
        self.init_project(['lcgcmt'])
        return

    def _download_git_submodules(self):
        'If gaudi is served from a git repo with a submodule per pacakge'
        url = self.url()
        if url[4] == '+': url = url[4:]
        log.info(self.name +' download')

        # Get super project
        self._git_clone(url,True)

        # Get release package
        self._git_checkout(self.tag(),self.rel_pkg())
        
        self.init_project(['lcgcmt'])

        # Get versions
        import cmt
        pkg_dir = os.path.join(self.proj_dir()+'/'+self.rel_pkg())
        uses = cmt.get_uses(pkg_dir,self.env(pkg_dir))
        for use in uses:
            #print 'use:',use.name,use.project,use.directory,use.version
            if use.project == 'gaudi' and use.directory == '':
                if '*' in use.version:
                    log.info('Skipping %s %s'%(use.name,use.version))
                    continue
                self._git_checkout(use.version,use.name)
                pass
            continue
        return

    def _git_clone(self,url,submodules=False):
        import fs,git
        target = fs.projects()+'/gaudi'
        if os.path.exists(target):
            log.info('Directory already exists, skipping clone to: %s'%target)
            return

        fs.goto(fs.projects(),True)
        git.clone(url,'gaudi')
        fs.goback()

        if submodules:
            fs.goto(os.path.join(fs.projects(),'gaudi'),True)
            git.submodule('init')
            git.submodule('update')
            fs.goback()

        return

    def _git_checkout(self,tag,pkg=""):
        import fs,git
        fs.goto(os.path.join(fs.projects(),'gaudi',pkg))

        lbranches,rbranches = git.branches()
        if tag in lbranches:
            git.checkout(tag)
        else:
            git.checkout('origin/'+tag,tag)

        fs.goback()
        return

