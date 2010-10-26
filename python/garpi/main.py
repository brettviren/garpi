#!/usr/bin/env python

class Garpi:
    '''
    Main object controlling installation.
    '''

    def __init__(self):
        
        from garpi.config import cli
        self.cli = cli

        from garpi import sanity
        sanity.check()

        self.projects = []

        projects = cli.cfg('projects',section='main')
        if 'lcgcmt' not in projects:
            raise ValueError, 'lcgcmt is a required project'
        for pname in projects:
            if pname == 'lcgcmt':
                from garpi.lcgcmt import Lcgcmt
                self.lcgcmt = Lcgcmt()
                self.projects.append(self.lcgcmt)
            elif pname == 'gaudi':
                from garpi.gaudi import Gaudi
                self.gaudi = Gaudi()
                self.projects.append(self.gaudi)
            else:
                from garpi.projects import Project
                self.projects.append(Project(pname))
            continue        
        
        webcache = cli.cfg('webcache',default=None,section='main')
        if webcache:
            import os
            os.environ['GARPI_WEBCACHE'] = ' '.join(webcache)

        return

    def run(self):
        'Apply command line arguments'
        
        if not self.cli.args: return

        try:
            cmd = self.cli.args[1]
        except IndexError:
            self.cli.parser.error("No command line argument given")
            return
        try:
            args = self.cli.args[2:]
        except IndexError:
            args = []

        func = eval("self.do_%s"%cmd)
        if args: func(args)
        else: func()

    def do_help(self):
        'Print list of commands and their brief documentation strings.'
        for methname in dir(self):
            if 'do_' not in methname: continue
            cmdname = methname[3:]
            meth = eval('self.%s'%methname)
            print '%s:\n\t%s\n'%(cmdname,meth.__doc__)
            continue
        return


    def do_setup(self):
        'Create basic setup scripts'
        import garpi.setup
        garpi.setup.init()
        return

    def do_install_prerequisites(self):
        self.do_install_cmt()
        if self.cli.file.has_section('git'):
            self.do_install_git()
        return

    def do_install_cmt(self,what="all"):
        'Install cmt'
        if what == "all": what = ["download","unpack","build","setup"]
        if type(what) == type(""): what = [what]

        from garpi import cmt

        for cmd in what:
            func = eval("cmt.%s"%cmd)
            func()
            continue
        return

    def do_install_git(self,what="all"):
        'Install git'
        if what == "all": what = ["download","unpack","build","setup"]
        if type(what) == type(""): what = [what]

        from garpi import git

        for cmd in what:
            func = eval("git.%s"%cmd)
            func()
            continue
        return


    def do_print_projects(self):
        'Print out what projects are configured'
        for proj in self.projects:
            print proj.name,
        print

    def do_get_projects(self,projlist=None):
        'Get the source code for all projects'
        if projlist:
            projects = map(lambda x: Project(x))
        else:
            projects = self.projects
        for proj in projects:
            proj.download()
        return        

    def do_init_projects(self,projlist=None):
        'Initialize projects'
        if projlist:
            projects = map(lambda x: Project(x))
        else:
            projects = self.projects

        deps = []
        for proj in projects:
            proj.init_project(deps)
            deps.append(proj.name)
        return        

    def do_lcgcmt(self):
        'undocumented'
        self.lcgcmt.download()
        self.lcgcmt.init_project()
        return

    def do_show_tags(self):
        'undocumented'
        print '\n'.join(self.lcgcmt.tags())
        return

    def do_print_cmtconfig(self):
        'Print the CMTCONFIG of this native host'
        print self.lcgcmt.cmtconfig()
        return

    def do_test_cmtconfig(self,cmtconfig = None):
        'Test given CMTCONFIG or one from environment'
        import os
        if not cmtconfig: 
            cmtconfig = os.getenv('CMTCONFIG',None)
            if cmtconfig is None: 
                print 'No CMTCONFIG given and none in the environment'
                return
            cmtconfig = [cmtconfig]
        for cc in cmtconfig:
            print 'Testing "%s"'%cc
            self.lcgcmt.test_cmtconfig(cc)
            print '%s ok.'%cc
        return

    def do_init_cmtconfig(self,cmtconfig = None):
        'Add setting CMTCONFIG to setup project.'
        import os
        if cmtconfig is None:
            cmtconfig = os.getenv('CMTCONFIG',None)
        if cmtconfig is None:
            cmtconfig = self.lcgcmt.cmtconfig()
        if cmtconfig is None:
            raise ValueError, 'Unable to get good CMTCONFIG'
        if isinstance(cmtconfig,list): cmtconfig = cmtconfig[0]
        print 'Saving CMTCONFIG =',cmtconfig
        import fs
        base = fs.setup()

        # Bourne Shell
        sh = open(os.path.join(base,'20_cmtconfig.sh'),'w')
        sh.write('''#!/bin/sh
CMTCONFIG=%s
export CMTCONFIG
'''%cmtconfig)
        sh.close()

        # C(rappy) Shell
        csh = open(os.path.join(base,'20_cmtconfig.csh'),'w')
        csh.write('''#!/bin/csh
setenv CMTCONFIG %s
'''%cmtconfig)
        csh.close()
        return        

    def do_print_externals(self):
        'Print externals required by configured projects'
        pkglist = self.externals()
        print ' '.join(pkglist)
        return

    def do_get_externals(self,pkglist=None):
        'Get the source files for the given list of externals, or all required ones'
        if not pkglist:
            pkglist = self.externals()

        for pkg in pkglist:
            self.lcgcmt.get_package_source(pkg)
        

    def do_externals(self,pkglist=None):
        'Build given list of externals, or all required ones'
        if not pkglist:
            pkglist = self.externals()

        for pkg in pkglist:
            self.lcgcmt.build_package(pkg)

        return

    def externals(self):
        'return ordered list of all externals needed by listed projects'
        if self.cli.opts.externals: 
            return self.cli.opts.externals

        return self.lcgcmt.all_externals(self.projects[1:])

    def do_projects(self,projects=None):
        'Build projects in order listed in configuration file'
        projlist = self.projects
        if projects:
            names = map(lambda x: x.name,self.projects)
            projlist = []
            for name in projects:
                ind = names.index(name)
                projlist.append(self.projects[ind])
                continue
            pass
        for proj in projlist:
            print 'Building %s'%proj.name
            proj.config()
            proj.make()
            continue
        return
            

    def do_pack(self, args):
        'Pack current intall into a tar file'
        try:
            tarfilename = args[0]
        except IndexError:
            raise ValueError, 'No tar file name given.'
        

        import binary
        packer = binary.Packer(tarfilename,self.projects,self.externals())
        tar = packer()
        return

    def do_unpack(self, args):
        'Unpack given packed tar file'
        try:
            tarfilename = args[0]
        except IndexError:
            raise ValueError, 'No tar file name given.'

        import binary
        unpacker = binary.Unpacker(tarfilename,self.projects)
        unpacker()
        return

    def do_emit_setenv_config(self, filename=None):
        'Emit configuration suitable for use by garpi-setenv'
        import fs, os

        if not filename: filename='/dev/stdout'
        fp = open(filename,'w')

        fp.write('[defaults]\n')
        fp.write('base_release = %s\n'%fs.projects())

        projects = list(self.projects)
        projects.reverse()
        for p in projects:
            rp = p.rel_pkg()
            if rp:
                fp.write('release_package = %s\n'%os.path.join(p.name,rp))
                break
            continue
        fp.close()
        return


    pass


if '__main__' == __name__:
    garpi = Garpi()
    garpi.run()
