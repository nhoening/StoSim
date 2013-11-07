
Currently refactoring - please do not yet install!

What is this?
--------------------
StoSim runs stochastic simulations.

You write the actual simulation, but stosim relieves you of:
- Arranging runs for all combinations of your dependent variables.
- Distributing workload across several CPUS, even on different machines. The latter
  works in a local environment with shared home directories or on a PBS cluster.
- Generating nice paper-ready plots and T-Tests from the results.

There are example simulations in the "example" folder and you can find extensive documentation at
http://homepages.cwi.nl/~nicolas/stosim/


Dependencies
--------------------
You need Python 2.7, or 2.6 if you install the argparse module locally.
You need my fjd program to schedule simulations across CPUs.
For plotting, you need gnuplot and epstopdf (some tips: for debian-linux, epstopdf 
is currently in the "texlive-extra-utils" package. On OSX, install gwTex via i-installer).
For T-Tests, you need Gnu R installed.


Running a simulation
--------------------
Place an experiment configuration and your simulation code in a folder of your choice (see basic example).
Call ./stosim.py --folder <path-to-your-experiment-folder>
You can leave the --folder option away if stosim.conf is in the current directory.
The results will be put in the "data" directory, in your folder 
(but if you like the plotting capabilities of StoSim you might never have to look there).


Enjoy.
