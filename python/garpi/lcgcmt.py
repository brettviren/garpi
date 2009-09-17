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
        sets = self.sets()
        try:
            return sets['CMTCONFIG'].strip()
        except KeyError:
            pass

        from exception import CommandFailure
        for macro in ['host-cmtconfig','LCG_platform']:
            try:
                return self.macro(macro).strip()
            except CommandFailure:
                pass
            continue

        return None

    def test_cmtconfig(self,cmtconfig):
        import cmt
        rel_path = os.path.join(self.proj_dir(),self.rel_pkg(),'cmt')
        extra_env = cmt.env(rel_path)
        suggested = cmt.macro('host-cmtconfig',extra_env=extra_env,dir=rel_path).strip()
        extra_env['CMTCONFIG'] = cmtconfig
        found = cmt.macro('host-cmtconfig',extra_env=extra_env,dir=rel_path).strip()
        platform = cmt.macro('LCG_platform',extra_env=extra_env,dir=rel_path).strip()
        assert cmtconfig == found, 'Error: given CMTCONFIG not supported: "%s" != "%s"'%(cmtconfig,found)
        assert cmtconfig == platform, 'Error: CMTCONFIG will differ from platform: "%s" != "%s"'%(cmtconfig,basesystem)
        return


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
CMTEXTRATAGS=garpi
export CMTEXTRATAGS
        '''%(fs.base(),fs.name()))
        sh.close()

        # C(rappy) Shell
        csh = open(os.path.join(base,'10_lcgcmt.csh'),'w')
        csh.write('''#!/bin/csh
setenv SITEROOT %s
setenv CMTPROJECTPATH %s
setenv CMTEXTRATAGS garpi
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

    def builder_externals(self,pkgs,exclusions=[]):
        '''Take an ordered list of LCG_Interface packages, return an
        ordered list of LCG_Interface packages.  If an input package
        has dependencies they will be inserted before the input
        package name.'''
        from util import log

        ret = []
        for pkg in pkgs:
            builder_dir = self.builder_directory(pkg)
            if not builder_dir:
                log.warn('Unable to find builder directory for "%s"'%pkg)
                continue
            builder_pkg = os.path.basename(builder_dir)
            rel_dir = os.path.join('LCG_Builders',builder_pkg)

            externals = self.externals(package=rel_dir,exclusions=exclusions)
            #print 'builder_pkg=',builder_pkg,' has externals:',externals
            for ext in externals:
                if ext == pkg: continue

                ext_dir = self.builder_directory(ext)
                if not ext_dir:
                    log.warn('Unable to find builder directory for "%s"'%ext)

                if ext in ret: continue
                ret.append(ext)
                continue

            if pkg not in ret:
                ret.append(pkg)
            continue

        return ret

    def build_package(self,pkg):
        '''
    for cmd in get config make install
    do
        echo "$pkg: running \"cmt pkg_$cmd\""
        cmt pkg_$cmd
        check_cmd
    done
        '''
        import fs
        fs.assure(os.path.join(fs.external(),'tarFiles'))
        fs.assure(os.path.join(fs.external(),'build/LCG'))

        dir = self.builder_directory(pkg)
        from exception import InconsistentState
        if dir is None: 
            raise InconsistentState('No builder directory for "%s"'%pkg)
        
        print 'Building %s in %s'%(pkg,dir)

        pkg = os.path.basename(dir)
        cmtdir = os.path.join(dir,'cmt')

        import fs
        fs.goto(cmtdir)

        env = self.env(os.path.join('LCG_Builders',pkg))
        
        import cmt
        for what in ['get','config','make','install']:
            print '\t%s'%what
            cmt.cmt('pkg_%s'%what,extra_env=env,dir=cmtdir)

        
        fs.goback()
        return

