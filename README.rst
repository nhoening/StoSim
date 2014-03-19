
What is this?
--------------------

StoSim is a light-weight framework for parameterised stochastic simulations. The researcher provides the simulation code (written in the programming language of his/her choice), 
but StoSim takes over a lot of tedious work from there on. StoSim can

* create all necessary computation jobs (from lists of parameter settings)
* execute these jobs on available CPUs (only your computer, the local network or PBS computation cluster)
* handle stochastic repetition of settings and seeding of randomness (for repeatable experiments) 
* analyse the results with graphical plots and T-tests (it is easy to analyse results made with specific parameter settings)
* back up code and results (to be able to go back to important milestones)

You can find extensive documentation at http://homepages.cwi.nl/~nicolas/stosim/ and example simulations in the "example" folder.


Installation/Dependencies
---------------------------
the short answer::

    pip install stosim

More details and help are in the documentation.


Dependencies
---------------
* You need Python 2.7, or 2.6 if you install the argparse module locally.
* For plotting, you need gnuplot and epstopdf.
* For T-Tests, you need Gnu R installed.

More details and help are in the documentation.


Running a simulation: A quick overview
---------------------------------------
Place an experiment configuration (stosim.conf) and your simulation code in a folder of your choice (see basic example).
Call::

    stosim --folder <path-to-your-experiment-folder>

You can leave the --folder option away if stosim.conf is in the current directory.
The results will be put in the "data" directory, in your folder 
(but if you like the plotting capabilities of StoSim you might never have to look there).

