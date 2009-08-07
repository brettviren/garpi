'''
Things related to LCGCMT project that are not related to projects in general..  
'''

from projects import Project
import os

class Lcgcmt(Project):
    def __init__(self):
        Project.__init__(self,"lcgcmt")
        return

    def project_externals(self,project):
        '''Determine external dependencies of the given project.  The
        project is assumed to be downloaded.  Returns an ordered
        list.'''
        return []


    def cmtconfig(self):
        'Return the auto-determined CMTCONFIG value.'
        import cmt
        rel_path = os.path.join(self.proj_dir(),self.rel_pkg(),'cmt')
        extra_env = cmt.env(rel_path)

        sets = cmt.sets(extra_env=extra_env,dir=rel_path)
        try:
            return sets['CMTCONFIG']
        except KeyError:
            pass

        from exception import CommandFailure
        for macro in ['host-cmtconfig','LCG_platform']:
            try:
                return cmt.macro(macro,extra_env=extra_env,dir=rel_path)
            except CommandFailure:
                pass
            continue

        return 'unsupported-configuration'

    def init_project(self,deps=[]):
        'Initialize the LCGCMT project'
        import fs,os
        setupdir = fs.setup()
        fs.assure(setupdir)

        # Bourne Shell
        sh = open(os.path.join(base,'10_lcgcmt.sh'),'w')
        sh.write('''#!/bin/sh
CMTPROJECTPATH=%s
CMTCONFIG=%s
export CMTPROJECTPATH,CMTCONFIG
        '''%(fs.projects(),self.cmtconfig()))
        sh.close()

        # C(rappy) Shell
        csh = open(os.path.join(base,'10_lcgcmt.csh'),'w')
        csh.write('''#!/bin/csh
setenv CMTPROJECTPATH %s
setenv CMTCONFIG %s
        '''%(fs.projects(),self.cmtconfig()))
        csh.close()
        return
