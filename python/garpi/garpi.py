#!/usr/bin/env python

import os,sys

class Garpi:
    '''
    Main object controlling installation.  It is passed to each state
    handler.
    '''

    def __init__(self,argv=None):
        self.machine = None
        self._env = os.environ
        if argv: 
            self.process_args(argv)
            self.load_states()
        return

    def process_args(self,argv):
        '''
        Command line control of main GARPI installation object. 

        Any command line arguments that may also be set in a
        configuration file take precedence.

        Use "--help" for details.
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


        from util import log, setup
        setup(options.log_file)
        log.setLevel(options.log_level)

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
        self.machine = StateMachine("machine.state")

        import states
        for state in states.__all__:
            state = eval('states.'+state)
            #print state
            try:
                state = state()
            except TypeError: pass
            state.register(self.machine)
            continue
        self.machine.add_state("DONE", None, end_state=1)

        return

    def start(self):
        'Start the build'
        self.machine.run(self,self.opts.starting_state)

    pass



    
if '__main__' == __name__:
    garpi = Garpi(sys.argv)
    garpi.start()
