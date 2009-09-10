#!/usr/bin/env python

class Garpi:
    '''
    Main object controlling installation.
    '''

    def __init__(self):
        
        from garpi import sanity
        sanity.check()

        from garpi.config import cli
        self.cli = cli

        self.projects = []

        from garpi.lcgcmt import Lcgcmt
        self.lcgcmt = Lcgcmt()
        self.projects.append(self.lcgcmt)

        from garpi.gaudi import Gaudi
        self.gaudi = Gaudi()
        self.projects.append(self.gaudi)

        projects = eval(cli.file.get('projects','projects'))
        for pname in projects:
            if pname in ['lcgcmt','gaudi']: continue
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

    def do_setup(self):
        import garpi.setup
        garpi.setup.init()
        return

    def do_cmt(self,what="all"):
        if what == "all": what = ["download","unpack","build","setup"]
        if type(what) == type(""): what = [what]

        from garpi import cmt

        for cmd in what:
            func = eval("cmt.%s",cmd)
            func()
            continue
        return

    def do_print_cmtconfig(self):
        print self.lcgcmt.cmtconfig()
        return

    def do_print_externals(self):
        pkglist = self.externals()
        print ' '.join(pkglist)
        return

    def do_externals(self,pkglist=list()):
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
        for proj in self.projects:
            for ext in proj.externals():
                if ext not in pkgs:
                    pkgs.append(ext)
                    pass
                continue
            continue
        return pkgs


if '__main__' == __name__:
    garpi = Garpi()
    garpi.run()
