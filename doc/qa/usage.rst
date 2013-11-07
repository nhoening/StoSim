.. _usage:

How to use StoSim
==================


Quick How-To
------------
  1. Place a file called ``stosim.conf`` and the code to run your simulation in a folder of your choice.
  2. In the file stosim.conf (copy `the one from the basic example <https://github.com/nhoening/stosim/raw/master/examples/basic/stosim.conf>`_ to start), set the name of your executable.
  3. Call ``./stosim.py``. Or, if you also have this shortcut I created for myself (see :ref:`get`), you can go to your simulation folder and simply type ``stosim``
  4. You should then see some output on the screen about what StoSim is doing and, if it went well, find results (the logfiles your executable wrote) in the "data" directory, in your folder (but if you like the plotting capabilities of StoSim you might never look there). Plots go in the "plots" directory.

.. note:: There are several tutorials in this documentation which describe how to use StoSim in depth. Start with :ref:`basic_example`.

All commands at a glance
-------------------------

Usage
^^^^^^
You can call StoSim like this::

    stosim [-h] [-d] [--simfolder PATH]
                     [--simulations [<NAME> [<NAME> ...]]] [--run] [--list] [--more]
                     [--plots [FIGURE [FIGURE ...]]] [--ttests]``


Commands/Arguments
^^^^^^^^^^^^^^^^^^^

This is a more detailled overview over the possible optional arguments::

  -h, --help            show this help message and exit
  -d                    overwrite old log files without confirmation  
  --folder PATH         Path to simulation folder (this is where you keep your
                        stosim.conf), defaults to "."
  --simulations [<NAME> [<NAME> ...]]
                        names of subsimulations (the filenames of their
                        configuration files without the ".conf" ending).
  --run                 Only run, do not get (remote) results and do not
                        analyse.
  --list                List number of runs made so far, per configuration.
  --more                Add more runs to current state of config and data.
  --plots [FIGURE [FIGURE ...]]
                        Make plots (needs gnuplot and eps2pdf installed). Add
                        indices of figures as arguments if you only want to
                        generate specific ones.
  --ttests              Run T-tests (needs Gnu R installed).


.. note:: Each command line option can be shortened, as long as it's
          recognisable from other short forms. So ``--p`` instead of ``--plots``
          also works.´´


