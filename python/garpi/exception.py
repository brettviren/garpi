'''
Exceptions garpi code might throw.
'''

class InconsistentState(Exception):
    'Thrown when garpi state is found to be inconsistent with reality'
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    pass

class CommandFailure(Exception):
    'Thrown when a command fails to run successfully'
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    pass
