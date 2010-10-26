#!/usr/bin/env python

'''
Wrapper for CMT installation and use
'''

from util import untar, log
import fs, os

def ver():
    from config import cli
    return cli.file.get('cmt','cmt_version')

def tgz():
    return "CMT%s.tar.gz"%ver()

def base_url():
    from config import cli
    return cli.file.get('cmt','cmt_site_url')

def url():
    return '%s/%s/%s'%(base_url(),ver(),tgz())

def srcdir():
    return fs.external() + '/CMT/'+ver()

def download():
    'Download CMT source tar file into external area.'
    log.info('downloading cmt tar file')
    target = "%s/%s"%(fs.external(),tgz())
    from get import get
    from exception import InconsistentState
    target = get(url(),target)
    if not os.path.exists(target):
        raise InconsistentState,'Tar file does not exist: %s%s'%(os.getcwd(),tgz())
    return target

def unpack():
    'Unpack the previously downloaded tarfile'
    log.info('unpacking cmt source')
    target = srcdir()
    if os.path.exists(target):
        log.info('CMT appears to already be unpacked in %s'%(target))
        return target
    fs.goto(fs.external(),True)
    untar(tgz())
    return target

def unique_path(path):
    'Return a path with duplicates removed, keeping order, first wins.'
    ret = []
    for chunk in path.split(':'):
        if chunk not in ret:
            ret.append(chunk)
            pass
        continue
    return ':'.join(ret)

def update_env(old,new):
    '''
    Update environ dictionary "old" with the contents of "new".
    PATH-like variables are handled.  Also returns the updated old.
    '''
    for k,v in new.iteritems():
        new_v = v
        if old.has_key(k):
            if 'PATH' in k or ':' in old[k] or ':' in v: # is path-like 
                new_v = unique_path(old[k] + ':' + v)
                pass
            pass
        old[k] = new_v
        continue
    return old


def merge_env(envs):
    '''
    Return a merged environ dictionary made from the given list of
    environ dictionaries.  Any path-like variables will be merged such
    that the final order is that of the envs that contain them with
    duplicates removed.
    '''
    ret = {}
    for env in envs:
        if not ret:
            ret.update(env)
            continue
        update_env(ret,env)
    return ret


_environ = None
def env():

    """Return the environment after sourcing CMT's setup.sh.  It
    assumes a cmt.build() has been called.  """

    global _environ
    if _environ is not None:
        return _environ

    from command import source
    mgrdir = os.path.join(srcdir(),'mgr')
    #print 'cmt.env: source %s/setup.sh'%mgrdir
    _environ = source('./setup.sh',dir=mgrdir)
    return _environ


def build():
    'Build CMT in previously unpacked cmt.srcdir().'
    log.info('building cmt')

    fs.goto(os.path.join(srcdir(),'mgr/'))

    from command import cmd,make,source

    def stupid_hack():
        # quick hack for v1r22.  this really doesn't belong here!
        fp = open("../source/cmt_std.h")
        for line in fp:
            if 'climits' in line: return
            continue
        fp.close()
        fp = open("../source/cmt_std.h","a")
        fp.write("#include <climits>\n")
        fp.close()
        return
    stupid_hack()

    # always run this in case user does something silly like move the
    # installation somewhere else 
    cmd('./INSTALL')

    environ = env()
    cmtexe = '%s/%s/cmt'%(srcdir(),environ['CMTCONFIG'])
    if os.path.exists(cmtexe):
        log.info('CMT appears to already have been built: %s'%cmtexe)
    else:
        log.info('CMT rebuild, not found at: %s'%cmtexe)
        make(env=environ)
    return cmtexe

def setup():
    'Add CMT setup scripts to the setup directory.'
    setup = srcdir() + '/mgr/setup'
    fs.assure(fs.setup())
    fs.goto(fs.setup())
    def do_link(ext):
        if os.path.exists('00_cmt'+ext): 
            os.remove('00_cmt'+ext)
        import shutil
        shutil.copy(setup+ext,'00_cmt'+ext)
    for ext in ['.sh','.csh']:
        do_link(ext)
    return fs.setup() + '/00_cmt.sh'
        
#------ build above, usage below --------#

def cmt(cmdstr='', environ=None, dir=None, output=False):

    """Run 'cmt [cmdstr]'.  By default the environment will be that
    provided by cmt.env(pkgdir=dir) unless an explicity environment is
    given via the environ arg.  The dir and output options are passed
    to command.cmd."""

    if not environ:
        environ = env()

    from command import cmd, source
    try:
        ret = cmd('cmt '+cmdstr, env=environ, dir=dir, output=output)
    except OSError,msg:
        print msg
        print 'PATH:'
        for p in environ['PATH'].split(':'):
            print '\t',p
        #for k,v in environ.iteritems():
        #    print '"%s" = "%s"'%(k,v)
        raise
    return ret

def show(what, environ=None, delim = '=', dir=None):

    '''Run "cmt show what".  Return dictionary of result.  The
    argument environ and dir are passed to cmt.cmt().'''

    res = cmt('show '+what, environ = environ, dir=dir, output = True)
    ret = {}
    for line in res.split('\n'):
        line = line.strip()
        comma = line.find(delim)
        # the bounds on val are moved in by 1 char to avoid the "'"s
        # that surround the value.
        key,val = line[:comma],line[comma+2:-1]
        ret[key] = val
        continue
    return ret

def macros(environ=None, dir=None):

    '''Return all defined macros and their definitions.  The environ
    and dir args are passed to cmt.cmt()'''

    return show('macros',environ=environ,dir=dir)

def macro(name, environ=None, dir=None):

    '''Return the value for the given macro name and their definitions.
    The environ and dir args are passed to cmt.cmt()'''

    cmdstr = 'show macro_value '+name
    return cmt(cmdstr, environ=environ, dir=dir, output=True)

def sets(environ=None, dir=None):

    '''Return all defined sets and their definitions.  The environ and
    dir args are passed to cmt.cmt()'''

    return show('sets', environ=environ, dir=dir)

def tags(environ=None, dir=None):

    '''Return all defined tags and their sources.  The environ and dir
    args are passed to cmt.cmt()'''

    return show('tags', environ=environ, delim=' ', dir=dir)

def parse_project_file(file):
    fp = open(file)
    res = {}
    for line in fp.readlines():
        line = line.strip()
        if not line: continue
        if line[0] == '#': continue
        words = line.split()
        if not res.has_key(words[0]): 
            res[words[0]] = []
        res[words[0]].append(" ".join(words[1:]))
        continue
    return res

class UsedPackage:
    def __init__(self,name,depth,private=False,directory="",version="",project=""):
        self.name=name
        self.depth=depth
        self.private=private
        self.directory=directory
        self.version=version
        self.uses=list()
        self.project = project
        log.debug(self)
        return

    def __str__(self):
        return  '%s %s %s %s %s %s %s'%(self.name,self.depth,self.private,
                                        self.version,self.project,self.directory,
                                        map(lambda x: x.name,self.uses))

def reachable_packages(pkg, environ=None, dir=None):
    lines = cmt('show packages', environ=environ, dir=dir, output=True)
    ret = {}
    for line in lines.split('\n'):
        line = line.strip()
        if not line: continue
        try:
            name,version,path = line.split()
        except ValueError:
            print 'can not unpack "%s", skipping'%line
            continue
        if os.path.exists(path+'/'+version):
            ret[name] = path+'/'+version
        else:
            ret[name] = path
    return ret

def package_version(pkg_dir, environ=None):
    out = cmt("show version", environ=environ, dir=pkg_dir+'/cmt', output=True)
    #print 'SHOW VERSION: dir="%s" output="%s"'%(pkg_dir,out)
    return out.strip()

def package_project(pkg_dir, environ=None):
    out = cmt("show projects", dir=pkg_dir+'/cmt', environ=environ, output=True)
    for line in out.split('\n'):
        line = line.strip()
        if line[0] == '#': 
            print line
            continue
        return line.split()[0].strip()
    return None

def get_uses(pkg_dir,environ):
    'Return the packages that the package at the given directory uses'
    
    this_pkg = os.path.basename(pkg_dir)
    this_ver = package_version(pkg_dir, environ)
    this_project = package_project(pkg_dir, environ)
    #print pkg_dir,'is in project',this_project

    log.debug("pkg =",this_pkg,"ver =",this_ver,"project =",this_project)

    uses = [UsedPackage(this_pkg,0,False,"",this_ver,this_project)]
    pack2proj = {this_pkg:this_project}

    #...debugging...
    #for kv in environ.iteritems(): print '"%s" --> "%s"'%kv
    #print 'CMTPATH="%s"'%environ['CMTPATH']
    #print 'pkg_dir="%s", projects="%s"'%(pkg_dir,fs.projects())

    res = cmt("show uses",environ,pkg_dir+'/cmt',True)
    #print 'SHOW USES: "%s"'%res

    for line in res.split('\n'):
        line = line.strip()
        words = line.split(' ')
        if len(words) == 1: continue
        if line[0] != '#': 
            pack = words[1]
            # CMT packages printed out in a non-standard way, and we
            # don't need them anyways.
            if len(pack) > 2 and pack[:3] == 'CMT': continue
            proj = words[4][:-1]
            if proj[-1] == '/': proj = proj[:-1]
            proj = os.path.basename(proj)
            pack2proj[pack] = proj
            #print pack,"==>",proj
            continue
        log.debug('words =',words)
        depth = 1
        for w in words[1:]:     # count spaces
            if w: break
            depth += 1
        if words[depth] != 'use': continue
        #print words
        name = words[depth+1]
        ver = words[depth+2]
        try:
            dir = words[depth+3]
        except IndexError:
            dir = ""
        private = False
        try:
            if words[depth+4] == '(private)':
                private = True
        except IndexError:
            pass

        depth = 1+(depth-1)/2
        uses.append(UsedPackage(name,depth,private,dir,ver))
        continue
    
    stack = []
    for u in uses:
        try:
            u.project = pack2proj[u.name]
        except KeyError:
            u.project = "Unknown"
        if not stack:
            log.debug('stack: %s'%u)
            stack.append(u)
            continue
        while stack and u.depth-stack[-1].depth != 1: 
            tmp = stack.pop()
            log.debug('pop: %s(%d) for %s(%d)'%(tmp.name,tmp.depth,u.name,u.depth))
            continue
        if stack:
            stack[-1].uses.append(u)
            log.debug('add uses: %s'%stack[-1])
        stack.append(u)
        log.debug('stack: %s'%u)

    return uses

class Project:
    def __init__(self,path,current=False,deps=None):
        self.path = path
        self.file = parse_project_file(path + "/cmt/project.cmt")
        self.deps = deps
        if self.deps is None: self.deps = list()
        self.current = current
        #self.used_packages = get_uses("%s/%s"%(path,self.file['container']))
        return

def get_projects(path):
    s,res = cmt("show projects",path)
    p = {}
    depnames = []
    curproj = None
    for line in res.split('\n'):
        line = line.strip()
        (name,ver,junk,path,rest) = line.split(" ",4)
        rest = rest.strip().split()
        if p.has_key(name): continue
        path = path[:-1]        # strip off ")"

        project = Project(path)
        if rest[0] == "(current)":
            project.current = True
            curproj = project
            del rest[0]
            pass
        for d in rest:
            pc,n = d.split("=")
            if pc == "C": project.deps.append(n)
            pass
        p[name] = project
        continue
    for name,project in p.iteritems():
        deps = []
        for dname in project.deps:
            deps.append(p[dname])
        project.deps = deps
        continue
    return p

