'''
Things related to LCGCMT project that are not related to projects in general..  
'''

from projects import Project
import os

class Lcgcmt(Project):
    def __init__(self):
        Project.__init__(self,"lcgcmt")
        return

    def cmtconfig(self):
        'Return an auto-determined CMTCONFIG value.'
        import cmt
        rel_path = os.path.join(self.proj_dir(),self.rel_pkg(),'cmt')
        extra_env = cmt.env(rel_path)

        sets = cmt.sets(extra_env=extra_env,dir=rel_path)
        try:
            return sets['CMTCONFIG'].strip()
        except KeyError:
            pass

        from exception import CommandFailure
        for macro in ['host-cmtconfig','LCG_platform']:
            try:
                return cmt.macro(macro,extra_env=extra_env,dir=rel_path).strip()
            except CommandFailure:
                pass
            continue

        return None

    def init_project(self,deps=[]):
        'Initialize the LCGCMT project'
        import fs,os
        setupdir = fs.setup()
        fs.assure(setupdir)

        base = fs.setup()

        # Bourne Shell
        sh = open(os.path.join(base,'10_lcgcmt.sh'),'w')
        sh.write('''#!/bin/sh
CMTPROJECTPATH=%s
export CMTPROJECTPATH
        '''%fs.projects())
        sh.close()

        # C(rappy) Shell
        csh = open(os.path.join(base,'10_lcgcmt.csh'),'w')
        csh.write('''#!/bin/csh
setenv CMTPROJECTPATH %s
        '''%fs.projects())
        csh.close()
        return

    def builder_directory(self,pkgname):
        builders = os.path.join(self.proj_dir(),'LCG_Builders')
        for thing in os.listdir(builders):
            path = os.path.join(builders,thing)
            if not os.path.isdir(path):
                #print 'Not a dir: "%s"'%path
                continue
            if thing.lower() == pkgname.lower():
                return path
            #print 'Not matching "%s" != %s'%(thing,pkgname)
            continue
        return None

    def build_package(self,pkg):
        return

