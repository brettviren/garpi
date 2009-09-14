#!/bin/bash

# This script pulls a subset of generally useful pacakges from LHCb's
# CVS repository.  It works by first downloading certain *Sys packages
# and using their cmt/requirements files to get the proper versions of
# their dependencies.

# It strictly assumes that CVSROOT is defined externally to:
#
# CVSROOT=:pserver:anonymous@isscvs.cern.ch:/local/reps/lhcb
#
# This is so one can make use of "cvsconnect" to re-use the CVS
# connection.  This will *greatly* speed up the running.  Use
# cvsconnect like:
#
# cvsconnect :pserver:anonymous@isscvs.cern.ch:/local/reps/lhcb /path/to/lhcb.sh

# Choose an LhcbSys release from the announcements here:
# http://lhcb-release-area.web.cern.ch/LHCb-release-area/DOC/lhcb/
lhcb_sys=v26r3
# Choose the Panoramix from announcements here:
# http://lhcb-release-area.web.cern.ch/LHCb-release-area/DOC/panoramix/
pano_sys=v16r4
# To get GaussSys version, check
# http://lhcb-release-area.web.cern.ch/LHCb-release-area/DOC/gauss/
# and pick one that depends on the closest version of LHCbSys to
# the one above.
gauss_sys=v36r2


real_cvsroot=:pserver:anonymous@isscvs.cern.ch:/local/reps/lhcb

# This is used for populating bv's git repository and isn't
# necessarily something others will want to use.
fix_cvsroot () {
    dir=$1; shift

    if [ "$CVSROOT" = ":ext:dummy@dummy.invalid:/local/reps/lhcb" ] ; then
	for target in $(find $dir -name CVS -type d -print) ; do
	    echo $real_cvsroot > $target/Root
	done
    fi    
}

# This is used for populating bv's git repository and isn't
# necessarily something others will want to use.
fetch () {
    pkg=$1 ; shift
    ver=$1 ; shift

    if [ -d $pkg ] ; then
	echo "Package $pkg already exists, skipping"
	return
    fi

    echo "Getting $pkg version $ver"
    #return
    cvs get -r $ver $pkg
    fix_cvsroot $sdir
}

# This is used for populating bv's git repository and isn't
# necessarily something others will want to use.
fetch_group () {
    sys=$1 ; shift
    ver=$1 ; shift

    if [ -d $sys ] ; then
	echo "Driver $sys already exists"
    else
	fetch $sys $ver
    fi

    for path in $@
    do
	echo "Processing $path"
	echo $path | tr '/' ' '| while read sdir spkg ; do 
	    if [ "$sdir" = "." ] ; then sdir=""; fi
	    grep "^use $spkg[[:space:]]" $sys/cmt/requirements | grep "[[:space:]]$sdir" | while read u p v d rest ; do
		#echo "p=$p v=$v d=$d"
		if [ -n "$d" ] ; then d="$d/" ; fi
		fetch $d$p $v
		done
	done
    done
}


# This is used for populating bv's git repository and isn't
# necessarily something others will want to use.
fetch_latest () {

    set -- `getopt l:p:g: $*`

    # Packages we need.
    #
    base_pkgs="./GaudiConf ./GaudiObjDesc"
    base_pkgs="$base_pkgs Det/DetDesc Det/DetDescCnv Det/DetDescSvc"
    base_pkgs="$base_pkgs Det/DetDescChecks Det/Magnet"
    base_pkgs="$base_pkgs Tools/XmlTools Kernel/LHCbKernel Kernel/LHCbMath"
    base_pkgs="$base_pkgs Event/GenEvent Event/EventBase Event/MCEvent"

    visu_pkgs="Vis/SoDet Vis/SoUtils Vis/SoHepMC Vis/Panoramix Vis/VisSvc"
    visu_pkgs="$visu_pkgs Vis/OSCONX Vis/OnXSvc Vis/RootSvc Vis/SoStat"
    
    giga_pkgs="Tools/ClhepTools Sim/GiGa Sim/GiGaCnv Sim/GaussTools"

    fetch_group LHCbSys $lhcb_sys $base_pkgs

    fetch_group PanoramixSys $pano_sys $visu_pkgs

    fetch_group GaussSys $gauss_sys $giga_pkgs
}


remove_unwanted () {
    git rm -r Event/MCEvent
    git rm -r Vis/OSCONX
    git rm Sim/GiGaCnv/src/component/GiGaCnvFunctors.h
    git rm Sim/GiGaCnv/src/component/Particle2Definition.cpp
    git rm Sim/GiGaCnv/src/component/Particle2Definition.h
    git rm Sim/GiGaCnv/src/component/Particle2Particle.cpp
    git rm Sim/GiGaCnv/src/component/Particle2Particle.h
    git rm Sim/GiGaCnv/src/component/Point2Vertex.h
    git rm Sim/GiGaCnv/src/component/PrimaryVertex2Vertex.h
    git rm Sim/GiGaCnv/src/component/Trajectory2Particle.h
    git rm Sim/GiGaCnv/src/component/Vertex2Vertex.cpp
    git rm Sim/GiGaCnv/src/component/Vertex2Vertex.h
}

fetch_latest
remove_unwanted
