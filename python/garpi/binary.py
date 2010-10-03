#!/usr/bin/env python
'''
pack [options] tarfilename - pack an installation into a tar file
'''

class Packer(object):
    def __init__(self,args):
        from optparse import OptionParser
        parser = OptionParser(usage=__doc__,add_help_option=False)

        parser.add_option('-r','--include-repository',default=False,action='store_true',
                          help='Include version control directories.')
        parser.add_option('-e','--externals',type='string',default='all',
                          help='Which externals to include, "all", "none" or comma separated list')
        parser.add_option('-p','--projects',type='string',default='all',
                          help='Which projects to include, "all", "none" or comma separated list')
        parser.add_option('-N','--no-act',default=False,action='store_true',
                          help='No action, simulate what would be done')
        opts,args = parser.parse_args(args=args)
        self.opts = opts
        if not opts.no_act:
            if not args:
                raise ValueError, 'No tar file name given.'
            self.tarfilename = args[0]
        self.project_objects = []
        self._make_project_objects()
        return

    def __call__(self):
        import tarfile
        if self.opts.no_act:
            self.tar = None
        else:
            self.tar = tarfile.TarFile.open(self.tarfilename,'w')

        self.pack_projects()
        self.pack_externals()
        self.pack_extra()
        return self.tar
        
    def _existing_projects(self):
        import fs, command
        ret = []
        projdir = fs.projects()
        out = command.cmd("find . -maxdepth 1 -type d -print",
                          dir=projdir, output=True)
        for line in out.split('\n'):
            pname = line[2:].strip()
            if not pname: continue
            if pname == 'setup': continue
            ret.append(pname)
            continue
        return ret

    def _make_project_objects(self):
        if self.project_objects: return
        if self.opts.projects.lower() == 'none': return
        pnames = None
        if self.opts.projects.lower() == 'all': 
            pnames = self._existing_projects()
        else:
            pnames = self.opts.projects.split(',')
        for pname in pnames:
            pname = pname.strip()
            if pname == 'lcgcmt':
                from garpi.lcgcmt import Lcgcmt
                self.lcgcmt = Lcgcmt()
                self.project_objects.append(self.lcgcmt)
            elif pname == 'gaudi':
                from garpi.gaudi import Gaudi
                self.gaudi = Gaudi()
                self.project_objects.append(self.gaudi)
            else:
                from garpi.projects import Project
                self.project_objects.append(Project(pname))
            continue
        return

    def _keeper(self,path):
        if not len(path): return False
        if path[-1] == '~': return False
        if path[-4:] == '.pyc': return False
        if '/genConf/' in path: return False

        if self.opts.include_repository: return True
        if '/.git/' in path: return False
        if '/.svn/' in path: return False
        if '/CVS/'  in path: return False
        return True


    def _project_files(self):
        import os, command, fs

        cmtconfig = os.getenv('CMTCONFIG')
        basedir = fs.base()

        grist = []
        for proj in self.project_objects:
            projdir = os.path.join(fs.projects(),proj.name)

            out = command.cmd("find . -type f -print",
                              dir=projdir, output=True)
            for path in out.split('\n'):
                if not self._keeper(path): continue

                if path[:2] == './': path = path[2:]
                path = os.path.join(projdir,path)
                path = path[len(basedir)+1:]

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
                    grist.append((linkname,pathname))
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
        projdir = fs.projects()[len(basedir)+1:]
        grist.append(os.path.join(projdir,'setup'))
        grist.append(os.path.join(projdir,'setup.sh'))
        grist.append(os.path.join(projdir,'setup.csh'))
        return grist

    def pack_projects(self):
        self.pack_files(self._project_files())
        return

    def _external_files(self):

        if self.opts.externals.lower() == 'none': return []

        if self.opts.externals.lower() == 'all':
            externals = self.lcgcmt.all_externals(self.project_objects[1:])
        else:
            externals = self.opts.externals.split(',')
            pass

        import os,fs,cmt
        base = fs.base()

        ret = []
        intdir = os.path.join(fs.projects(),'lcgcmt/LCG_Interfaces')
        for pkg in externals:
            intpkg = os.path.join(intdir,pkg,'cmt')
            home = cmt.macro(pkg + '_home', dir=os.path.join(intpkg))
            home = home[len(base)+1:] # make relative to base
            ret.append(home)
            continue
        return ret

    def pack_externals(self):
        self.pack_files(self._external_files())
        return

    def pack_files(self,filelist):
        for thing in filelist:
            if self.tar:
                self.tar.add(thing)
            else:
                print 'tar.add(%s)'%thing
            continue
        return

    def pack_extra(self):
        import os
        paths = []
        if self.opts.externals.lower() != 'none': 
            for what in ['CMT','git']:
                path = os.path.join('external',what)
                if os.path.exists(path):
                    paths.append(path)
                    pass
                continue
            pass
        self.pack_files(paths)
        return

            
