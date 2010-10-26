#!/usr/bin/env python

class Packer(object):
    '''
    pack [options] tarfilename - pack an installation into a tar file
    '''
    def __init__(self, tarfilename, project_objects, externals):
        from garpi.config import cli
        self.cli = cli

        for pobj in project_objects:
            if pobj.name == 'lcgcmt':
                self.lcgcmt = pobj
                break

        self.tarfilename = tarfilename
        self.project_objects = project_objects
        self.externals = externals
        return

    def __call__(self):
        import tarfile
        if self.cli.opts.no_act:
            self.tar = None
        else:
            self.tar = tarfile.TarFile.open(self.tarfilename, 'w')

        self.pack_projects()
        self.pack_externals()
        self.pack_extra()
        return self.tar
        
    def _keeper(self, path):
        if not len(path): return False
        if path[-1] == '~': return False
        if path[-4:] == '.pyc': return False
        if '/genConf/' in path: return False

        if self.cli.opts.include_repository: return True
        if '/.git/' in path: return False
        if '/.svn/' in path: return False
        if '/CVS/'  in path: return False
        return True


    def _project_files(self):
        import os, command, fs

        cmtconfig = os.getenv('CMTCONFIG')

        project_area = fs.projects()
        basedir = os.path.dirname(project_area)
        snip = len(basedir)+1

        grist = []
        for proj in self.project_objects:
            projdir = os.path.join(project_area, proj.name)

            out = command.cmd("find . -type f -print",
                              dir=projdir, output=True)
            for path in out.split('\n'):
                if not self._keeper(path): continue

                if path[:2] == './': path = path[2:]
                path = os.path.join(projdir, path)
                path = path[snip:]

                # Handle InstallArea special
                if '/InstallArea/' in path:
                    if path[-7:] != '.cmtref':
                        grist.append(path)
                        continue

                    # If not companion symlink, then give up and just add the file
                    linkname = path[:-7]
                    if not os.path.islink(path):
                        grist.append(path)
                        continue

                    # Resolve symlink and save both
                    pathname = readlink(linkname)
                    grist.append((linkname, pathname))
                    continue

                if cmtconfig in path: continue

                # ignore some common cruft
                if '/cmt/' in path:
                    if '.root' == path[-5:]: continue
                    if '.log' == path[-4:]: continue
                    if '.out' == path[-4:]: continue
                    filename = path.split('/')[-1]
                    if 'setup' in filename: continue
                    if 'cleanup' in filename: continue
                    if 'Makefile' == filename: continue

                grist.append(path)
                continue
            continue

        # some extra by hand
        projdir = fs.projects()[snip:]
        grist.append(os.path.join(projdir, 'setup'))
        grist.append(os.path.join(projdir, 'setup.sh'))
        grist.append(os.path.join(projdir, 'setup.csh'))
        return grist

    def pack_projects(self):
        self.pack_files(self._project_files())
        return

    def _external_files(self):

        import os, fs, cmt
        project_area = fs.projects()
        basedir = os.path.dirname(project_area)
        snip = len(basedir)+1
        #print snip, basedir, project_area

        ret = []
        intdir = os.path.join(project_area, 'lcgcmt/LCG_Interfaces')
        for pkg in self.externals:
            intpkg = os.path.join(intdir, pkg, 'cmt')
            environ = self.lcgcmt.env(intpkg)
            home = cmt.macro(pkg + '_home', environ=environ, dir=intpkg)
            #print intpkg, home
            home = home[snip:] # make relative to base
            ret.append(home)
            continue
        return ret

    def pack_externals(self):
        self.pack_files(self._external_files())
        return

    def pack_files(self, filelist):
        import os
        missing = []
        for thing in filelist:
            if self.tar:
                if os.path.exists(thing):
                    self.tar.add(thing)
                else:
                    missing.append(thing)
            else:
                print 'tar.add(%s)'%thing
            continue
        if missing:
            print 'Missed %d out of %d files:\n'%(len(missing), len(filelist))
            print '\n\t','\n\t'.join(missing)            
        return

    def pack_extra(self):
        import os
        paths = []
        if self.externals:
            for what in ['CMT','git']:
                path = os.path.join('external', what)
                if os.path.exists(path):
                    paths.append(path)
                    pass
                continue
            pass
        self.pack_files(paths)
        return

            
class Unpacker(object):
    '''
    unpack tarfilename - unpack an installation from its packed tar file
    '''

    def __init__(self, tarfilename, project_objects):
        from garpi.config import cli
        import os, fs
        self.tarfilename = tarfilename
        self.project_objects = project_objects

        if self.tarfilename[0] != '/':
            self.tarfilename = os.path.join(os.getcwd(), self.tarfilename)

        dstdir = cli.opts.unpack_directory
        if dstdir != '/':
            dstdir = os.path.join(os.getcwd(), cli.opts.unpack_directory)
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        self.dstdir = dstdir
        self.srcdir = os.path.dirname(fs.projects())
        self.cli = cli
        return

    def _unpack_tar(self):
        tarcmd = "tar -x"
        if 'gz' in self.tarfilename: tarcmd += "z"
        tarcmd += "f %s"%self.tarfilename
        from command import cmd
        cmd(tarcmd, dir=self.cli.opts.unpack_directory)
        return

    def _fix_cmt(self):
        import os, cmt
        from command import cmd
        newdir = os.path.join(self.dstdir,'external/CMT',cmt.ver(),'mgr')
        cmd('./INSTALL',env=None,dir=newdir)
        import shutil
        shutil.copy(os.path.join(newdir,'setup.sh'), os.path.join(self.dstdir,'projects/setup/00_cmt.sh'))
        shutil.copy(os.path.join(newdir,'setup.csh'), os.path.join(self.dstdir,'projects/setup/00_cmt.csh'))
        return

    def _fix_setup(self):
        from garpi import setup
        import os
        base = os.path.join(self.dstdir,'projects/setup')
        setup.dump_sh(base)
        setup.dump_csh(base)

        # this is ugly!
        def munge_script(ext,match):
            fname=os.path.join(base,'10_lcgcmt.%s'%ext)
            fp = open(fname)
            lines = fp.read().split('\n')
            fp.close()
            out = []
            for line in lines:
                if line[:len(match)] == match:
                    line = match+self.dstdir
                    pass
                out.append(line)
                continue
            fp = open(fname,"w")
            fp.write('\n'.join(out))
            fp.close()
            return

        munge_script("sh","SITEROOT=")
        munge_script("csh","setenv SITEROOT ")
        return

    def _fix_projects(self):
        import fs,os,cmt
        from command import source
        fs.goto(os.path.join(self.dstdir,'projects'))
        environ = source('./setup.sh')
        for pobj in self.project_objects:
            pdir = os.path.join(self.dstdir,'projects',pobj.name,pobj.rel_pkg(),'cmt')
            cmt.cmt("config",environ=environ,dir=pdir)
            pkgenv = source('./setup.sh',env=environ,dir=pdir)
            cmt.cmt("br cmt config",environ=pkgenv,dir=pdir)
        fs.goback()
            
    
    def __call__(self):
        self._unpack_tar()
        self._fix_cmt()
        self._fix_setup()
        self._fix_projects()
        
