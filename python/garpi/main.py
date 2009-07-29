#!/usr/bin/env python

import os,sys
from util import log

class Go:
    def __init__(self,garpi):
        self.garpi = garpi
        return

    def to(self,theDir):
        if not os.path.exists(theDir):
            os.makedirs(theDir)
        os.chdir(theDir)
        return theDir

    def external(self):
        'Go to the external directory'
        theDir = garpi.opts.base_directory + '/external'
        return self.to(theDir)

class Garpi:
    '''
    Main object controlling installation.  It is passed to each state
    handler.
    '''

    def __init__(self,argv):
        self.go = Go(self)
        self.machine = None
        self._env = os.environ

        self.process_args(argv)
        self.load_states()
        return

    def process_args(self,argv):
        '''
        Command line control of main GARPI installation object. 

        Any command line arguments that may also be set in a
        configuration file take precedence.

        Use "--help" for details of the options.

        '''
        from optparse import OptionParser
        import logging

        parser = OptionParser(usage = self.process_args.__doc__)
        parser.add_option('-c','--config-file',type='string',
                          help='Configuration file holding defaults')
        parser.add_option('-D','--dump-config',default=None,type='string',
                          help='Dump formatted configuration to given file, "-" for stdout.')
        parser.add_option('-s','--starting-state',default='START',type='string',
                          help='State to start in.')
        parser.add_option('-L','--log-level',default=logging.INFO,type='int',
                          help='Verbosity of logging');
        parser.add_option('-l','--log-file',default='garpi.log',type='string',
                          help='Specify a log file')
        parser.add_option('-n','--name',default='projects',type='string',
                          help='Name of directory to hold the projects')
        parser.add_option('-b','--base-directory',default=os.getcwd(),type='string',
                          help='Base directory holding project and external areas')

        (options,args) = parser.parse_args(args=argv)
        self.opts = options
        self.args = args

        # Get defaults 
        from ConfigParser import SafeConfigParser
        self.cfg = SafeConfigParser()
        if options.config_file:
            self.cfg.read(options.config_file)
        else:
            self._load_default_config()


        from util import log_maker
        log_maker.set_file(options.log_file)
        log_maker.set_level(options.log_level)

        if options.dump_config:
            if options.dump_config == '-':
                fp = sys.stdout
            else:
                fp = open(options.dump_config,'w')
            self.cfg.write(fp)

        return

    def setenv(self,var,val):
        os.putenv(var,val)
        self._env = os.environ
        return
        
    def _load_default_config(self):
        default = os.path.dirname(__file__) + '/default.cfg'
        if not os.path.exists(default):
            print 'Warning, could not find default configuration at',default
            return
        self.cfg.read(default)
        return

    def load_states(self):
        if self.machine: return

        from statemachine import StateMachine
        name = (self.opts.base_directory,self.opts.name)
        self.machine = StateMachine("%s/%s.state"%name)
        self.machine.corefile = '%s/%s.core'%name

        import states
        for state in states.__all__:
            state = eval('states.'+state)
            #print state
            try:
                state = state()
            except TypeError: pass
            state.register(self)
            continue
        self.machine.add_state("DONE", None, end_state=1)

        return

    def dump(self,fp):
        fp.write('env = ' + str(self._env) + '\n')
        fp.write("cfg = '''\n")
        self.cfg.write(fp)
        fp.write("\n'''\n")
        fp.write('opts = ' + str(self.opts) + '\n')
        fp.write('args = ' + str(self.args) + '\n')

    def start(self):
        'Start the build'
        log.info('Garpi starting')
        self.machine.run(self,self.opts.starting_state)
        log.info('Garpi build done')

    def cmd(self,cmd,env=None):
        log.info('running: %s'%cmd)
        from subprocess import Popen, PIPE, STDOUT

        try:
            proc = Popen(cmd,stdout=PIPE,stderr=STDOUT,env=env)
        except OSError,err:
            log.error_notrace(err)
            log.error_notrace('In directory %s'%os.getcwd())
            raise

        from util import log_maker
        old_format = log_maker.set_format('%(message)s')

        madadayo = True
        res = None
        while madadayo:
            line = proc.stdout.readline()
            res = proc.poll()
            if not line and res is not None: madadayo = False
            if line: log.info(line.strip())
            continue

        log_maker.set_format(old_format)

        if res is not 0:
            log.error('Command: %s failed with code %d'%(cmd,res))
            from exception import CommandFailure
            raise CommandFailure,res

    pass



    
if '__main__' == __name__:
    garpi = Garpi(sys.argv)
    garpi.start()
