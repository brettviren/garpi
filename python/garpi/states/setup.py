'''
Set up the main setup scripts
'''

class MainSetupScript:
    def __init__(self):
        return

    def register(self,garpi):
        self.garpi = garpi
        garpi.machine.add_state('SETUP_START',self.start)
        
    def dump_sh(self,base):
        sh = open(base+'.sh','w')
        sh.write('''
#!/bin/sh
base=%s
for thing in $base/*.sh 
do
    source $thing
done
'''%base)
        sh.close()
        return

    def dump_csh(self,base):
        csh = open(base+'.csh','w')
        csh.write('''
set base = %s
foreach thing (`ls $base/*.csh`)
    source $thing;
end;
'''%base)
        csh.close()

    def start(self,cargo):
        self.garpi.go.setup()   # make sure dir exists
        base = self.garpi.go.projects() + '/setup'
        self.dump_sh(base)
        self.dump_csh(base)
        return ('SETUP_DONE',cargo)
