#!/usr/bin/env python
'''
Functions to create main setup scripts and assist client code in
writing their own.
'''
        
def dump_sh(base):
    sh = open(base+'.sh','w')
    sh.write('''
#!/bin/sh
base=%s
for thing in $base/*.sh 
do
    . $thing
done
'''%base)
    sh.close()
    return

def dump_csh(base):
    csh = open(base+'.csh','w')
    csh.write('''
set base = %s
foreach thing (`ls $base/*.csh`)
    source $thing;
end;
'''%base)
    csh.close()

def init():
    import fs
    setupdir = fs.setup()
    fs.assure(setupdir)
    # Note, we use the setup directory name as the base name for
    # top-level setup files, this is just coincidence/convention
    dump_sh(setupdir)
    dump_csh(setupdir)

