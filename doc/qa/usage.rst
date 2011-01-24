.. _usage:

How to use Nicessa
==================

Quick How-To
------------
  1. Place an experiment.conf and the code to run your simulation in a folder of your choice.
  2. In the experiment.conf (copy `the one from the basic example <../../../examples/basic/experiment.conf>`_ to start), set the name of your executable.
  3. Call ``./experiment.py <path-to-your-experiment-folder>``. Or, if you also have this shortcut I created for myself (see :ref:`get`), you can go to your experiment folder and simply type ``nicessa .``
  4. You should now find results in the "data" directory, in your folder (but if you like the plotting capabilities of nicessa you might never look there). Plots go in the "plots" directory.

All commands at a glance
----------

Usage
^^^^^^
``experiment.py <path-to-experiment-folder> [--experiments=X,Y] [--run] [--check] [--results] [--plots] [--ttests] [--more] [--list]``

.. note:: The experiment folder is where you have your experiment.conf

.. note:: If you run things on remote servers you will need the Python library 'paramiko'

Commands
^^^^^^^^^^^^

--experiments
    names of subexperiments (without '.conf', e.g. 'exp1,exp2')
--run
    Only run, do not get (remote) results and do not analyse
--check
    Check state of remote computers
--results
    Get results from remote computers
--list
    List number of runs made so far, per configuration
--more
    Add more runs to current state of config and data
--plots
    Make plots (needs gnuplot and eps2pdf installed))
--ttests
    Run T-tests (needs R installed)

.. note:: Each command line option can be shortened, as long as it's
          recognisable from other short forms. So ``--p`` instead of ``--plots``
          also works, while ``--r`` does not, because it could mean ``--run`` as well as
          ``--results``. 


