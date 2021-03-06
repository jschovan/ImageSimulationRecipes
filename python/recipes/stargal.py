"""
Aim: 
====

To enable simple tests of star/galaxy separation algorithms. 

Summary: 
========

To test algorithms for separating stars and galaxies, we will
simulate separate images of fields of stars and galaxies using exactly
the same atmosphere/optics for each set of images. We are effectively
simulating the sky with only the stars, and then the same sky with only
the galaxies. 

We simulate one chip over 100 different realisations of the atmosphere.
No dithering or rotation of the camera is applied - the only thing
changing between the 100 realisations is the atmosphere and seeing. 
"""

# ======================================================================

import subprocess, time, os
import utensils

# ======================================================================

def stargal():

    # We want to run phosim for both stars and galaxies:
    
    for typ in ['msstars', 'bdgals']:
        
        # The input catalogue files are in this directory. 
        
        catfile = "stargal-"+typ+".pars"

        # The data in the input catalogues provided cover this chip.
        # Format: R is the raft coordinate
        #         S is the sensor coordinate
        #         This is the center raft (22), 
        #         and the top center chip (21). 
        
        sensor = "R22_S21" 


        # Get seeing and seeds for the 100 atmospheric realisations.
        # These were generated from opsim, and exist in a dat file in
        # this directory. 
        
        seeings, seeds  = [], []
        for aline in open("stargal-atmos.dat","r"):
            cols = aline.split()
            seeds.append(cols[0])
            seeings.append(cols[1])


        # Loop over the 100 atmospheric realisations: 
        
        for atm in range(1,100):

            # Name your work and output dirs. This allows many jobs to
            # run simultaneously without their working files bumping
            # into each other on the disk.  make sure you put in the
            # full path to the directories, not the relative path. 
            
            workdir = "/path/to/ImageSimulationRecipes/python/recipes/work_"+typ+"_"+sensor+"_atm"+str(atm)
            outdir = "/path/to/ImageSimulationRecipes/python/recipes/output_"+typ+"_"+sensor+"_atm"+str(atm)


            # Point out what we're doing:
            
            print "Running phosim over", typ, \
                  "for atmosphere realisation", atm

            # Check whether the work and output dirs exist. If so, 
            # empty them. If not, make them. phosim will fail if they 
            # don't exist. 
            
            utensils.makedir(workdir, replace=True, query=False)
            utensils.makedir(outdir, replace=True, query=False)

            # Write out a new catalogue file to your workdir.
            # This will contain the same objects as the orginal 
            # catalogue, and the same pointing/rotation angle etc, but 
            # will have new random seed and seeing parameters. 
            
            newcatfilename = workdir+"/cat-"+typ+"-atm"+str(atm)+".dat"
            newcatfile = open(newcatfilename,"w")
            for aline in open(catfile):
                if "SIM_SEED" in aline:
                    print >> newcatfile, "SIM_SEED", seeds[int(atm)]
                elif "Opsim_rawseeing" in aline:
                    print >> newcatfile, "Opsim_rawseeing", seeings[int(atm)]
                else:
                    print >> newcatfile, aline[:-1]                
            newcatfile.close()



            # Now you're all set! Run phosim over this catalogue file.
            # there are many options here depending on your setup/needs.
            # Note that here we specify the configuration file for no 
            # sky background.

            # To run it interactively from your phosim installation
            # directory:
            
            subcmd = ["./phosim", newcatfilename,  "-c", "examples/nobackground", "-s", sensor, "-w", workdir, "-o", outdir]

            # To run it interactively on the slac batch system, you need
            # to specify the architecture to be rhel60. This uses the
            # xlong queue; if you have bright stars you may need xxl.
            # You can probably get away with the long queue as-is.  note
            # that this also uses the SLAC installation of phosim. 

            # SLAC-specific setup: if you haven't already, you will need
            # to load the LSST environment via: source
            # /afs/slac/g/lsst/software/redhat6-x86_64-64bit-gcc44/DMstack/Winter2013-v6_2/loadLSST.csh
            # You may also run into problems with a specific
            # environmental variable that you shoudl unset via: unsetenv
            # LS_COLORS

            # subcmd = ["bsub", "-q", "xlong", "-o", workdir+"/log.log", "-R", "rhel60", "python", "/afs/slac/g/lsst/software/redhat6-x86_64-64bit-gcc44/phoSim/phosim-3.3.2/phosim.py", newcatfilename,  "-c", "examples/nobackground", "-s", sensor, "-w", workdir, "-o", outdir]

            subprocess.call(subcmd)

            # You may want to pause between jobs, especially if you're
            # submitting them to a batch system. 
            
            time.sleep(5)

# ======================================================================

if __name__ == '__main__':

    stargal()

# ======================================================================
