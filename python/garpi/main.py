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

        projects = eval(cli.file.get('projects','projects'))
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

        pkgs = []
        for proj in self.projects[1:]:
            direct = proj.externals()
            print 'Project %s has %d direct'%(proj.name,len(direct)),
            indirect = self.lcgcmt.builder_externals(direct)
            print 'and %d total externals'%len(indirect)
            for ext in indirect:
                print proj.name,ext,
                if ext in direct: print '(direct)'
                else: print '(indirect)'
                if ext not in pkgs:
                    pkgs.append(ext)
                    pass
                continue
            continue
        return pkgs


if '__main__' == __name__:
    garpi = Garpi()
    garpi.run()
