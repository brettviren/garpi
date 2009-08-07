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
    fs.goto(fs.external())
    untar(tgz())
    return target

def env():
    '''Return the environment after sourceing CMT's setup.sh.  This
    will fail if called before cmt.build() has been run.'''
    from command import source
    environ = source('./setup.sh',dir=srcdir()+'/mgr')
    return environ
            

def build():
    'Build CMT in previously unpacked cmt.srcdir().'
    log.info('building cmt')

    target = srcdir() + '/mgr/setup.sh'
    fs.goto(srcdir() + '/mgr/')

    from command import cmd,make,source
    if not os.path.exists(target):
        cmd('./INSTALL')

    environ = env()
    cmtexe = '%s/%s/cmt'%(srcdir(),environ['CMTCONFIG'])
    if os.path.exists(cmtexe):
        log.info('CMT appears to already have been built: %s'%cmtexe)
    else:
        make(env=environ)
    return cmtexe

def setup():
    'Add CMT setup scripts to the setup directory.'
    setup = srcdir() + '/mgr/setup'
    fs.goto(fs.setup())
    def do_link(ext):
        if os.path.exists('00_cmt'+ext): return
        os.symlink(setup+ext,'00_cmt'+ext)
    for ext in ['.sh','.csh']:
        do_link(ext)
    return fs.setup() + '/00_cmt.sh'
        
#------ build above, usage below --------#

def cmt(cmdstr='',extra_env={},dir=None,output=False):
    '''Run "cmt [cmdstr]".  The environment in which the cmt
    executable is run is initially composed of the application
    environment.  It is then modified by sourcing CMT's setup script.
    Finally, any extra_env that is passed in will be used to update
    the env in which the command is run.  The dir and output options
    are passed to command.cmd.'''
    from command import cmd,source
    environ = env()
    if extra_env: environ.update(extra_env)
    return cmd('cmt '+cmdstr,env=environ,dir=dir,output=output)

def show(what,extra_env={},delim = '='):
    'Run "cmt show what".  Return dictionary of result'
    res = cmt('show '+what,extra_env = extra_env, output = True)
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

def macros(extra_env={}):
    '''Return all defined macros and their definitions.  If any
    extra_env is given it will be added to what is needed just to
    setup cmt.'''
    return show('macros',extra_env=extra_env)

def sets(extra_env={}):
    '''Return all defined sets and their definitions.  If any
    extra_env is given it will be added to what is needed just to
    setup cmt.'''
    return show('sets',extra_env=extra_env)

def tags(extra_env={}):
    '''Return all defined tags and their sources.  If any extra_env is
    given it will be added to what is needed just to setup cmt.'''
    return show('tags',extra_env=extra_env,delim=' ')

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

def reachable_packages(pkg,extra_env={},dir=None):
    lines = cmt('show packages',extra_env=extra_env,dir=dir,output=True)
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

def package_version(pkg_dir,extra_env={}):
    return cmt("show version",extra_env=extra_env,dir=pkg_dir+'/cmt').strip()

def package_project(pkg_dir,extra_env={}):
    return cmt("show projects",dir=pkg_dir+'/cmt',extra_env=extra_env).split('\n')[0].strip()


def get_uses(pkg_dir):
    'Return the packages that the package at the given directory uses'
    
    path = pkg_dir + '/cmt'
    this_pkg = os.path.basename(pkg_dir)

    this_ver = package_version(this_pkg)
    this_project = package_project(this_pkg)

    log.debug("pkg =",this_pkg,"ver =",this_ver,"project =",this_project)

    uses = [UsedPackage(this_pkg,0,False,"",this_ver,this_project)]
    pack2proj = {this_pkg:this_project}

    if not os.path.exists(path+'/setup.sh'):
        cmt("config",dir=path)

    from command import source, cmd
    extra_env = source('./setup.sh',env=env(),dir=path)

    res = cmd("cmt show uses",env=extra_env,dir=path,output=True)

    for line in res.split('\n'):
        line = line.strip()
        words = line.split(' ')
        if len(words) == 1: continue
        if line[0] != '#': 
            pack = words[1]
            if pack == 'CMT': continue
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
    def __init__(self,path,current=False,deps=[]):
        self.path = path
        self.file = parse_project_file(path + "/cmt/project.cmt")
        self.deps = deps
        self.current = current
        self.used_packages = get_uses("%s/%s"%(path,self.file['container']))
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
