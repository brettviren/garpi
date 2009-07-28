def start(garpi):
    return ('CMT_DOWNLOAD',garpi)

def register(machine):
    machine.add_state('START',start)

