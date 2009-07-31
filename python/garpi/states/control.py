'''
The control states.  

These link up groups of states that perform related activities.  Each
related activity has an entry point named with GROUP_START and when
finished will leave things in the state named with GROUP_DONE with
"GROUP" replaced by the group name.

Groups include:

CMT - install CMT


'''

class StateLink:
    def __init__(self,machine,one,two):
        machine.add_state(one,self.link)
        self.next = two
        return
    def link(self,cargo):
        return (self.next,cargo)

def register(g):
    m = g.machine
    StateLink(m,'START','SETUP_START')
    StateLink(m,'SETUP_DONE','CMT_START')
    StateLink(m,'CMT_DONE','DONE')

def start(cargo):
    return ('SETUP_START',cargo)
def stop(cargo):
    return ('DONE',cargo)
