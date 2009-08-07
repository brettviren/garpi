'''
States for getting lcgcmt installed.
'''

class LcgcmtStates:
    def __init__(self):
        return

    def register(self,garpi):
        self.garpi = garpi
        garpi.machine.add_state('LCGCMT_START',self.start)

        return

    def start(self,cargo):
        return
