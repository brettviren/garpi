#!/usr/bin/env python
'''
A main class for garpi-setenv
'''

from config import Config
from command import source, cmd
import os,sys, pickle

class Main(object):
    def __init__(self,cfg,env=None):
        self.cfg = cfg
        if env is None: env = {}
        self.init_env = dict(env)
        self.env = dict(env)
        self.pre_cmdlist = []
        self.post_cmdlist = []
        return

    def __call__(self):
        'Run the program'
        if self.cfg.opts.test:
            self.test()
            return

        if self.cfg.opts.generate_scripts:
            self.gen_scripts()
            return

        if self.cfg.opts.remember_environment:
            self.save_env()

        if self.cfg.opts.unsetup: 
            self.revert_env()
            return

        try:
            level = self.cfg.opts.setup_level
        except AttributeError:
            return
        if level:
            self.setup_env(level)
            return
        
        sys.stderr.write('''
Looks like we did nothing.  
Did you want to set up the default base release?  Add '-l base'.  
Or, a specific release by name? '-l base -r NAME'.
Otherwise, rerun with '-h' to see more help.

''')
        return

    def test(self):
        'Print information about how we are currently set up'
        sys.stderr.write('# Base Release information:\n')
        try:
            sys.stderr.write('base_release = %s'%self.cfg.base_release)
        except AttributeError:
            sys.stderr.write('base_release is not set\n')
        else:
            if os.path.exists(self.cfg.base_release):
                sys.stderr.write(' (path exists)\n')
            else:
                sys.stderr.write(' (path does not exists)\n')

        try:
            sys.stderr.write('release_name = %s\n'%self.cfg.release_name)
        except AttributeError:
            sys.stderr.write('release_name is not set\n')
        else:
            section = self.cfg.release_name
            sys.stderr.write('\n[%s]\n'%section)
            if not self.cfg.cfg.has_section(section):
                sys.stderr.write('(no such section "%s")\n'%section)
            else:
                for k,v in self.cfg.cfg.items(section,vars=self.cfg.cfgvars):
                    if not v: continue
                    sys.stderr.write('%s = %s\n'%(k,v))
                    continue
                pass
            pass

        sys.stderr.write('\n#Personal Project information\n')
        try:
            sys.stderr.write('project_dir = %s'%self.cfg.project_dir)
        except AttributeError:
            sys.stderr.write('project_dir is not set\n')
        else:
            if os.path.exists(self.cfg.project_dir):
                sys.stderr.write(' (path exists)\n')
            else:
                sys.stderr.write(' (path does not exists)\n')
            
        try:
            sys.stderr.write('project_name = %s\n'%self.cfg.project_name)
        except AttributeError:
            sys.stderr.write('project_name is not set\n')
        else:
            section = self.cfg.project_name
            sys.stderr.write('\n[%s]\n'%section)
            if not self.cfg.cfg.has_section(section):
                sys.stderr.write('(no such section "%s")\n'%section)
            else:
                for k,v in self.cfg.cfg.items(section,vars=self.cfg.cfgvars):
                    if not v: continue
                    sys.stderr.write('%s = %s\n'%(k,v))
                    continue
                pass
            pass


        return
            
    def gen_scripts(self):
        'Generate scripts for user to source'
        prefix = self.cfg.opts.generate_scripts
        path = os.path.basename(prefix)
        if not os.path.exists(path):
            os.makedirs(path)

        name = self.cfg.opts.name_for_scripts

        sys.stderr.write('Generating %s.sh with name %s\n'%(prefix,name))
        bsh = open(prefix+'.sh','w')
        bsh.write('''#!/bin/sh
%s () {
    file="/tmp/%s.${USER}.$$"
    %s -s bash $* > $file ;
    while [ -n "$1" ] ; do 
        shift;
    done;
    source "$file"
    rm -f "$file"
}
'''%(name,name,os.path.abspath(sys.argv[0])))
        bsh.close()

        sys.stderr.write('Generating %s.csh\n'%prefix)
        csh = open(prefix+'.csh','w') # abomination
        csh.write('''#!/bin/csh
setenv SHELL /bin/tcsh
alias %s 'set file=/tmp/%s.${USER}.$$; %s -s tcsh \!* > ${file}; source ${file}; rm -f ${file}'
'''%(name,name,os.path.abspath(sys.argv[0])))

    def stored_env_filename(self):
        'Return filename to for stored env'
        ppid = os.getppid()
        name = self.cfg.name_for_scripts
        filename = '~/.%s.saved.%d'%(name,ppid)
        return os.path.expanduser(filename)

    def save_env(self):
        'Save initial environment.'
        filename = self.stored_env_filename()
        sys.stderr.write('Saving env to %s\n'%filename)
        if os.path.exists(filename):
            sys.stderr.write('Warning, overwriting %s\n'%filename)
        fp = open(filename,'w')
        pickle.dump(self.init_env,fp)
        fp.close
        sys.stderr.write('Saved starting environment to %s\n'%filename)
        return
        
    def revert_env(self):
        'Revert to inital environment if stored file found.'
        filename = self.stored_env_filename()
        if not os.path.exists(filename):
            sys.stderr.write('Error, no stored env file %s\n'%filename)
            sys.exit(1)
        fp = open(filename,'r')
        newenv = pickle.load(fp)
        fp.close()
        self.emit(newenv)
        return

    def setup_env(self,level):
        'Setup environment'
        try:
            meth = eval('self._setup_%s'%level.lower())
        except AttributeError:
            sys.stderr.write('Unknown setup level: "%s"'%level)
            sys.exit(1)

        fp = open('/dev/stdout','w')

        #sys.stderr.write('START PRE\n')
        self._setup_pre()
        self.emit_pre(fp)
        #sys.stderr.write('END PRE\n')

        #sys.stderr.write('START MAIN\n')
        meth()
        self.emit(self.env,fp)
        #sys.stderr.write('END MAIN\n')

        #sys.stderr.write('START POST\n')
        self._setup_post()
        self.emit_post(fp)
        #sys.stderr.write('END POST\n')

        return

    def _setup_cmds(self,cmds):
        'Incorporate pre/post env commands'
        if type(cmds) == type(""): cmds = eval(cmds)
        new_env = self.env
        cmdlist = []
        for cmd in cmds:
            chunk = cmd.split()
            if chunk[0] == 'set':
                sk,v = cmd.split('=')
                v = v.strip()
                v = os.path.expanduser(os.path.expandvars(v))
                s,k = sk.split()
                k = k.strip()
                #sys.stderr.write('DEBUG: "%s" "%s" "%s"\n'%(s,k,v))
                new_env[k.strip()] = v
                cmdlist.append(('set',(k,v)))
                continue
            if chunk[0] == 'source':
                sys.stderr.write('source %s\n'%chunk[1])
                new_env = source(chunk[1],env=new_env)
                cmdlist.append(('source',chunk[1:]))
                continue
            if chunk[0] == 'emit':
                sys.stderr.write('Warning: not yet supported: emit %s\n'%\
                                     (' '.join(chunk[1:])))
                cmdlist.append(('emit',chunk[1:]))
                continue
            print 'Unknown command: "%s"'%cmd
            continue
        self.env.update(new_env)
        return cmdlist

    def _setup_pre(self):
        'Setup any pre_env'
        try:
            pe = self.cfg.pre_env
        except AttributeError:
            return
        self.pre_cmdlist = self._setup_cmds(pe)

    def _setup_post(self):
        'Setup any post_env'
        try:
            pe = self.cfg.post_env
        except AttributeError:
            return
        self.post_cmdlist = self._setup_cmds(pe)

    def _setup_none(self):
        'Do no setup'
        return

    def _setup_cmt(self):
        'Do basic setup that brings in CMT.'
        path = self.cfg.base_release
        sys.stderr.write('source setup.sh in %s\n'%path)
        self.env = source('setup.sh',env=self.env,path=path)
        return

    def _setup_base(self):
        'Set up the base release'
        self._setup_cmt()
        path = self.cfg.base_release
        path = os.path.join(path,'dybgaudi/DybRelease/cmt')
        sys.stderr.write('source setup.sh in %s\n'%path)
        self.env = source('setup.sh',env=self.env,path=path)
        return
    
    def _setup_project(self):
        'Set up personal project'
        path = self.cfg.project_dir

        cmtprojectpath = os.path.dirname(path)
        try:
            cpp = self.env['CMTPROJECTPATH']
        except KeyError:
            cpp = cmtprojectpath
        else:
            cpp = cmtprojectpath + ':' + cpp
        self.env['CMTPROJECTPATH'] = cpp

        package = self.cfg.package
        path = os.path.join(path,package,'cmt')


        if not os.path.exists(path+'/setup.sh'):
            sys.stderr.write('Running "cmt config" in "%s"\n'%path)
            cmd('cmt config',env=self.env,path=path)
        # Do it twice. See bug #105
        sys.stderr.write('Sourcing setup.sh in "%s"\n'%path)
        self.env = source('setup.sh',env=self.env,path=path)
        self.env = source('setup.sh',env=self.env,path=path)
        return


    def emit_cmds(self,cmdlist,fp):
        shell = self.cfg.shell
        if 'csh' in shell:
            return self.emit_csh(cmdlist,fp)
        else:
            return self.emit_sh(cmdlist,fp)
        return None

    def emit_pre(self,fp):
        'Setup any pre_env'
        fp.write('# pre environment #\n')
        return self.emit_cmds(self.pre_cmdlist,fp)

    def emit_post(self,fp):
        'Setup any post_env'
        fp.write('# post environment #\n')
        return self.emit_cmds(self.post_cmdlist,fp)

    def emit(self,env,fp):
        'Print to file object the shell settings.'
        fp.write('# main environment #\n')
        cmds = []
        for k,v in env.iteritems():
            cmds.append(("set",(k,v)))
        shell = self.cfg.shell
        if 'csh' in shell:
            self.emit_csh(cmds,fp)
        else:
            self.emit_sh(cmds,fp)
        return

    def emit_csh(self,cmds,fp):
        'Print to file object the csh settings'
        for cmd,args in cmds:
            if cmd == "set": 
                fp.write('setenv %s "%s"\n'%(args[0],args[1]))
                continue
            self.emit_one_generic(cmd,args,fp)
            continue
        return

    def emit_sh(self,cmds,fp):
        'Print to file object the sh settings'
        for cmd,args in cmds:
            if cmd == "set": 
                fp.write('%s="%s";export %s\n'%(args[0],args[1],args[0]))
                continue
            self.emit_one_generic(cmd,args,fp)
            continue
        return

    def emit_one_generic(self,cmd,args,fp):
        if cmd == "source": 
            fp.write('source %s\n'%args[0])
            return
        fp.write('#unknown command "%s" args:"%s"\n'%(cmd,args))
        return
