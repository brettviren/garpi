'''
The control states.  

These link up groups of states that perform related activities.  Each
related activity has an entry point named with GROUP_START and when
finished will leave things in the state named with GROUP_DONE with
"GROUP" replaced by the group name.

Groups include:

CMT - install CMT


'''

garpi = None
def register(g):
    global garpi
    garpi = g
    g.machine.add_state('START',start)
    #...
    g.machine.add_state('CMT_DONE',stop)

def start(cargo):
    return ('CMT_START',cargo)
def stop(cargo):
    return ('DONE',cargo)
