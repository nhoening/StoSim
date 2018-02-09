
What is this?
--------------------

StoSim is a light-weight framework for parameterised stochastic simulations. The researcher provides the simulation code (written in the programming language of his/her choice), 
but StoSim takes over a lot of tedious work from there on. StoSim can

* create all necessary computation jobs (from lists of parameter settings)
* execute these jobs on available CPUs (only your computer, the local network or PBS computation cluster)
* handle stochastic repetition of settings and seeding of randomness (for repeatable experiments) 
* analyse the results with graphical plots and T-tests (it is easy to analyse results made with specific parameter settings)
* back up code and results (to be able to go back to important milestones)

You can find tutorials and extensive documentation at http://stosim.nicolashoening.de and example simulations in the "example" folder.


Installation/Dependencies
---------------------------
the short answer::

    pip install stosim

More details and help are in the documentation.


Dependencies
---------------
* You need Python 3.3+, 2.7, or 2.6 if you install the argparse module locally.
* Distributing jobs needs Unix Screens, so if the `screen` command is not available on your system, you need to install it, e.g. on Debian::
      sudo apt-get install screen
* To use the in-built plotting, you need gnuplot and epstopdf, e.g. on Debian::
      sudo apt-get install gnuplot texlive-extra-utils
* For T-Tests, you need Gnu R installed.

More details and help are in the documentation.


Running a simulation: A quick overview
---------------------------------------
Place an experiment configuration (stosim.conf) and your simulation code in a folder of your choice (see basic example in the examples folder).
Call::

    stosim
    
This assumes that you placed a configuration file describing your jobs (called `stosim.conf`) in the current folder.
It also assumes you want to run the jobs, and in addition perform T-Tests and make plots (if stosim.conf says how). So the above command is synonymous to::

    stosim --folder . --run --ttests --plots

The results will be put in the "data" directory, in your folder 
(but if you like the plotting/analysis capabilities of StoSim you might never have to look there).

One more example, where you know your stosim.conf is in a different folder and you only want to run::

    stosim --folder <path-to-your-experiment-folder> --run

There are more features, e.g. `--more` to add more stochastic runs, `--list` to inspect data or `--snapshot` to make a snapshots of results at a given time that can be loaded back later. Do check out the tutorials where you can learn more. 
