#!/usr/bin/env python
'''
Provide environment setup for base release and personal
projects.

Usage: 

  garpi-setup [options] [file.cfg ...]

More information at:

  http://www.phy.bnl.gov/trac/garpi/

'''
# Note: this doc string is for the command line

import os,sys
from ConfigParser import NoOptionError
import ConfigParser

ConfigParser.DEFAULTSECT = 'defaults'

class Config(object):
    '''
    Interface to configuration files and command line.
    '''

    def __init__(self,argv=None):
        from ConfigParser import SafeConfigParser
        self.cmdline_parser = None
        cfg = SafeConfigParser()
        config_files = []
        fromenv = os.getenv('GARPI_SETENV_RC')
        if fromenv: config_files.append(fromenv)
        config_files += [
            os.path.expanduser('~/.garpi-setenv.cfg'),
            './.garpi-setenv.cfg'
            ]
        read = cfg.read(config_files)
        self.cfg = cfg
        self.cfgvars = {}

        self.cmdline(argv)
        return

    def __getattr__(self,key):
        #print 'getattr("%s")'%key
        ret = None
        if key == 'base_release': 
            ret = self.resolve_value(key,self.resolve_section('release_name',key))
        elif key == 'project_dir' or key == 'package': 
            ret = self.resolve_value(key,self.resolve_section('project_name',key))
        elif key == 'pre_env' or key == 'post_env':
            if self.opts.setup_level == 'base':
                ret = self.resolve_value(key,self.resolve_section('release_name',key))
            elif self.opts.setup_level == 'project':
                ret = self.resolve_value(key,self.resolve_section('project_name',key))
            else:
                raise AttributeError,'No such attribute "%s" for setup level "%s"'%\
                    (key,self.opts.setup_level)
        else:
            ret = self.get(key)
        if ret is None: 
            raise AttributeError,'No such attribute "%s"'%key

        return os.path.expanduser(os.path.expandvars(ret))

    def resolve_section(self,section_variable,variable_name):
        '''
        Find section that provides given variable name.
        '''
        #sys.stderr.write('\t...resolve_section("%s","%s")\n'%(section_variable,variable_name))

        # first see if the given section_variable is resolved through
        # the command line.
        try:
            section = self.cfgvars[section_variable]
            #sys.stderr.write('\t...trying section [%s] for "%s"\n'%(section,variable_name))
            if not self.cfg.has_section(section): 
                #print 'No such section [%s]'%section
                raise KeyError
        except KeyError:
            pass
        else:
            return section

        # Next check if the section_variable is resolved through the
        # default section.
        try:
            section = self.get(section_variable,section=ConfigParser.DEFAULTSECT)
            if not self.cfg.has_section(section):
                raise KeyError
        except KeyError:
            pass
        else:
            return section

        # Finally, hope it is in the default section
        return ConfigParser.DEFAULTSECT

    def resolve_value(self,variable_name,section):
        #sys.stderr.write('\t...resolve_value("%s","%s")\n'%(variable_name,section))
        val = self.get(variable_name,section=section)
        if val: return val
        if section != ConfigParser.DEFAULTSECT:
            return self.resolve_value(variable_name,ConfigParser.DEFAULTSECT)
        return None

    def get(self,key,default=None,section=ConfigParser.DEFAULTSECT):
        try:
            return self.cfg.get(section,key,vars=self.cfgvars)
        except NoOptionError:
            return default
        except TypeError,err:
            sys.stderr.write(str(err)+'\nInterpolation variables:\n')
            for k,v in self.cfgvars.iteritems(): sys.stderr.write('%s = %s\n'%(k,v))
            raise
            
        
    def _shell_ext(self):
        'set shell_ext cfg var based on shell'
        shell = self.cfgvars['shell']
        if  shell == 'csh' or shell == 'tcsh':
            self.cfgvars['shell_ext'] = 'csh'
        else:
            self.cfgvars['shell_ext'] = 'sh'
        return self.cfgvars['shell_ext']
        
    def _project_name(self):
        'Force setup_level to be project if project has been specified'
        pn = self.cfgvars['project_name']
        if pn:
            self.opts.setup_level = 'project'
        return pn

    def cmdline(self,argv):
        #print 'cmdline(%s)'%argv
        from optparse import OptionParser
        parser = OptionParser(usage=__doc__,add_help_option=False)
        
        # Fill cfgvars with hard coded defaults.  These should only
        # contain values that can be set/used in the config files
        self.cfgvars['opt_or_dbg'] = 'dbg'
        self.cfgvars['release_name'] = self.get('release_name')
        self.cfgvars['shell'] = self.get('shell')
        self._shell_ext()
        self.cfgvars['project_name'] = self.get('project_name')

        # Command line version of config file options
        parser.add_option('','--opt-or-dbg',type='string',default='dbg',
                          help='Set opt_or_dbg value if used in configuration files')
        parser.add_option('-O','--optimize',
                          action='store_const',dest='opt_or_dbg',const="opt")
        parser.add_option('-g','--debug',
                          action='store_const',dest='opt_or_dbg',const="dbg")

        parser.add_option('-r','--release-name',type='string',default=self.cfgvars['release_name'],
                          help='Set the release_name')

        parser.add_option('-s','--shell',type='string',default=self.cfgvars['shell'],
                          help='Explicitly set the shell')

        parser.add_option('-p','--project-name',type='string',default=self.cfgvars['project_name'],
                          help='Name of a personal project to set up')

        # Command line only command line
        parser.add_option('-l','--setup-level',type='string',default="base",
                          help='Emit setup code to given level (none, cmt, base, project)')

        parser.add_option('-R','--remember-environment',action='store_true',default=False,
                          help='Save env before emitting new env to allow one to undo the settings.')
                          
        parser.add_option('-u','--unsetup',action='store_true',default=False,
                          help='Emit previously saved environment, if possible.')

        parser.add_option('-t','--test',action='store_true',default=False,
                          help='Print out what configuration would have been used.')

        parser.add_option('-S','--generate-scripts',type='string',default="",
                          help='Give a prefix for .sh and .csh scripts to be generated.')
        parser.add_option('-N','--name-for-scripts',type='string',default="garpi-setenv",
                          help='Give a name to use for the setup shell function/alias when generating scripts.')


        parser.add_option('-h','--help',action='store_true',default=False,
                          help='Print out this help message')

        opts,args = parser.parse_args(args=argv)
        self.opts = opts

        if opts.help:
            parser.print_help(file=sys.stderr)
            sys.exit(0)

        # update cfgvars with non-None values and only for existing keys 
        for k,v in opts.__dict__.iteritems():
            if v is None: continue
            if self.cfgvars.has_key(k):
                self.cfgvars[k] = v
            continue

        # Set any dependent variables
        self._shell_ext()
        self._project_name()

        # Get rid of any pre-exising None values
        tmp = {}
        for k,v in self.cfgvars.iteritems():
            if v: tmp[k]=v
        self.cfgvars = tmp

        # treat any remaining arguments as more configuration files
        if args: self.cfg.read(args)

        self.cmdline_parser = parser

        return
    pass

