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
SITEROOT=%s
export SITEROOT
CMTPROJECTPATH=$SITEROOT/%s
export CMTPROJECTPATH
        '''%(fs.base(),fs.name()))
        sh.close()

        # C(rappy) Shell
        csh = open(os.path.join(base,'10_lcgcmt.csh'),'w')
        csh.write('''#!/bin/csh
setenv SITEROOT %s
setenv CMTPROJECTPATH %s
        '''%(fs.base(),fs.name()))
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

    def _get_package(self,env,dir):
        'Get the package source tar file'
        import cmt
        cmt.cmt('pkg_get',extra_env=env,dir=dir)

    def build_package(self,pkg):
        '''
    for cmd in get config make install
    do
        echo "$pkg: running \"cmt pkg_$cmd\""
        cmt pkg_$cmd
        check_cmd
    done
        '''
        dir = self.builder_directory(pkg)
        from exception import InconsistentState
        if not dir: InconsistentState('No builder directory for "%s"'%pkg)
        
        dir += '/cmt'

        import fs
        fs.goto(dir)

        import cmt
        env = cmt.env(dir)
        
        self._get_package(env,dir)
        
        fs.goback()
        return

