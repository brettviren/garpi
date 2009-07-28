# based on:
# http://www.ibm.com/developerworks/library/l-python-state.html

class StateMachine:
    corefile = 'statemachine.core'

    def __init__(self,statefile = None):
        self.handlers = {}
        self.endStates = []
        self.statefile = statefile
        return

    def add_state(self, name, handler, end_state=0):
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def persistentState(self):
        '''Return [state,status] from persistent file.'''
        if self.statefile is None: return None

        try:
            fp = open(self.statefile,"r")
        except IOError:
            return None
        return fp.readline().strip().split()

    def recordState(self,state,status,msg=None):
        if self.statefile is None: return

        fp = open(self.statefile,"w")
        line = state+' '+status
        fp.write(line + '\n')
        if msg: fp.write(msg + '\n')
        #print line
        fp.close()
        return

    def run(self, cargo, startState=None):
        if startState is None:
            startState = self.persistentState()[0]

        if startState is None:
            raise ValueError, "no initial state"

        if not self.endStates:
            raise ValueError, "no final states given"

        state = startState
        while True:
            if state in self.endStates:
                self.recordState(state,'ENDED')
                break 

            try:
                handler = self.handlers[state]
            except KeyError:
                raise ValueError,'Unregistered state: %s'%state

            self.recordState(state,'ENTERED')

            try:
                (newState, cargo) = handler(cargo)
            except Exception,err:
                print 'State handler for %s failed: %s'%(state,err)
                self.recordState(state,'FAILED',str(err))
                import pickle, gzip
                
                core = gzip.GzipFile(StateMachine.corefile,"w")
                pickle.dump(state,core)
                pickle.dump(cargo,core)
                core.close()
                print 'core dumped'
                raise Exception,err
            else:
                self.recordState(state,'EXITED')

            state = newState
            continue
        return

