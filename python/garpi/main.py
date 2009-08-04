#!/usr/bin/env python

import os,sys
from util import log,goto

class Dir:
    def __init__(self,garpi):
        self.garpi = garpi

    def external(self):
        return self.garpi.opts.base_directory + '/external'

    def projects(self):
        return self.garpi.opts.base_directory + '/' + self.garpi.opts.name

    def setup(self):
        return self.projects() + '/setup'

class Go:
    def __init__(self,garpi):
        self.garpi = garpi
        self.dir = Dir(garpi)
        return

    def to(self,theDir): 
        return goto(theDir)

    def external(self):
        'Go to the external directory'
        return self.to(self.dir.external())

    def projects(self):
        'Go to the directory holding projects'
        return self.to(self.dir.projects())

    def setup(self):
        'Go to the setup directory'
        return self.to(self.dir.setup())

class Garpi:
    '''
    Main object controlling installation.  It is passed to each state
    handler.
    '''

    def __init__(self,argv):
        self.go = Go(self)
        self.dir = Dir(self)
        self.machine = None
        self._env = os.environ

        import config
        self.cfg = config.file
        self.opts = config.opts
        self.args = config.args

        self.load_states()
        return

    def setenv(self,var,val):
        os.putenv(var,val)
        self._env = os.environ
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

    pass



    
if '__main__' == __name__:
    garpi = Garpi(sys.argv)
    garpi.start()
