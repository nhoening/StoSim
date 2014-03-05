.. _usage:

How to use StoSim
==================


Quick How-To
------------
  1. Place a file called ``stosim.conf`` and the code to run your simulation in a folder of your choice. In stosim.conf (copy `the one from the basic example <https://github.com/nhoening/stosim/raw/master/examples/basic/stosim.conf>`_ to start), set the name of your executable.
  2. Type ``stosim`` and hit Enter
  3. You should then see some output on the screen about what StoSim is doing and, if it went well, find results (the logfiles your executable wrote) in the "data" directory, in your folder (but if you like the plotting capabilities of StoSim you might never look there). Plots go in the "plots" directory.

.. note:: There are several tutorials in this documentation which describe how to use StoSim in depth. Start with :ref:`basic_example`.


All commands at a glance
-------------------------

Usage
^^^^^^
You can call StoSim like this::


    $ stosim --help
    usage: stosim [-h] [--folder PATH] [--simulations [NAME [NAME ...]]] [--run]
                [--check] [--resume] [--kill] [--list] [--more]
                [--plots [FIGURE [FIGURE ...]]] [--ttests] [-k] [-d]

Commands/Arguments
^^^^^^^^^^^^^^^^^^^

This is a more detailled overview over the possible optional arguments::

    -h, --help            show this help message and exit
    --folder PATH         Path to simulation folder (this is where you keep your
                          stosim.conf), defaults to "."
    --simulations [NAME [NAME ...]]
                          names of subsimulations (the filenames of their
                          configuration files, with or without the ".conf"
                          ending).
    --run                 Only run, do not analyse.
    --status              Check status of simulations.
    --resume              Resume control of simulation scheduling.
    --snapshot            Make a snapshot of current state (in the stosim-snapshots directory)
    --kill                Kill simulations.
    --list                List number of runs made so far, per configuration.
    --more                Add more runs to current state of config and data.
    --plots [FIGURE [FIGURE ...]]
                          Make plots (needs gnuplot and eps2pdf installed). Add
                          indices of figures as arguments if you only want to
                          generate specific ones.
    --ttests              Run T-tests (needs Gnu R installed).
    -k                    keep tmp analysis files.
    -d                    delete old data without confirmation.

.. note:: Each command line option can be shortened, as long as it's
          recognisable from other short forms. So ``--p`` instead of ``--plots``
          also works.´´


Debugging
----------------------------

A very important use case: The results are not coming in as expected. A likely scenario is this: the plots can't be created becuase your executable didn't write data, most likely because there is a bug somewhere. Where to look for system output to start investigation?

You can inspect the output of all the simulation workers in this directory::
    
    ~/.fjd/<your-project-name>/screenlogs
    
There will be one logfile per cpu (a "worker") that was running jobs for you. Because StoSim uses ``fjd`` for scheduling workers and ``fjd`` uses the shared home directory for all its configs and logs, this even works when you told StoSim to use several computers (see :ref:`remote_example` for an example on that).