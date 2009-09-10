'''
Command line arguments and configuration file.

This module provides a class to process command line options and
arguments and load the configuration file, either the default one or
one specified on the command lines.

Through the resulting object one can access the results

config.cli.file - a ConfigParser instance
config.cli.opts - command options from OptionParser
config.cli.args - command line arguments

'''

import sys,os



class CommandLineInterface:
    def __init__(self,argv):
        self.process_args(argv)

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
                          help='Name used to identify this build, will name the sub directory of --base-directory')
        parser.add_option('-b','--base-directory',default=os.getcwd(),type='string',
                          help='Base directory holding project and external areas')
        parser.add_option('-E','--externals',default=None,type='string',
                          help='Explicitly list externals (single name or Python list)')

        (options,args) = parser.parse_args(args=argv)
        self.parser = parser
        self.opts = options
        self.args = args

        # fix up options
        if self.opts.base_directory[0] != '/': 
            self.opts.base_directory = os.getcwd() + '/' + self.opts.base_directory
        if self.opts.log_file[0] != '/':
            self.opts.log_file = self.opts.base_directory + '/' + self.opts.log_file
        if self.opts.externals:
            if self.opts.externals[0] == "[":
                self.opts.externals = eval(self.opts.externals)
            else:
                self.opts.externals = [self.opts.externals]
            pass

        # Get defaults 
        from ConfigParser import SafeConfigParser
        self.file = SafeConfigParser()
        if options.config_file:
            self.file.read(options.config_file)
        else:
            self.load_default_config()


        from util import log_maker
        log_maker.set_file(options.log_file)
        log_maker.set_level(options.log_level)

        if options.dump_config:
            if options.dump_config == '-':
                fp = sys.stdout
            else:
                fp = open(options.dump_config,'w')
            self.file.write(fp)

        return

    def load_default_config(self):
        default = os.path.dirname(__file__) + '/default.cfg'
        if not os.path.exists(default):
            print 'Warning, could not find default configuration at',default
            return
        self.file.read(default)
        return

cli = CommandLineInterface(sys.argv)
