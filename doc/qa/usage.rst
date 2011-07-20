.. _usage:

How to use Nicessa
==================


Quick How-To
------------
  1. Place an nicessa.conf and the code to run your simulation in a folder of your choice.
  2. In the nicessa.conf (copy `the one from the basic example <http://www.assembla.com/code/nicessa/subversion/nodes/trunk/examples/basic/nicessa.conf>`_ to start), set the name of your executable.
  3. Call ``./nicessa.py <path-to-your-simulation-folder>``. Or, if you also have this shortcut I created for myself (see :ref:`get`), you can go to your simulation folder and simply type ``nicessa .``
  4. You should now find results in the "data" directory, in your folder (but if you like the plotting capabilities of nicessa you might never look there). Plots go in the "plots" directory.

.. note:: There are several tutorials in this documentation which describe how to use Nicessa in depth.

All commands at a glance
-------------------------

Usage
^^^^^^
``nicessa.py <path-to-simulation-folder> [--simulations=X,Y] [--run] [--check] [--results] [--plots] [--ttests] [--more] [--list] [--show-screen=HOST,CPU]``

.. note:: The simulation folder is where you have your nicessa.conf

.. note:: If you run things on remote servers you will need the Python library 'paramiko'

Commands
^^^^^^^^^^^^

--simulations
    names of sub-simulation configurations (without '.conf', e.g. 'sim1,sim2')
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
--show-screen
    Show current output of a remote screen, e.g. '--show-screen=1,3' shows cpu 3 on host 1"

.. note:: Each command line option can be shortened, as long as it's
          recognisable from other short forms. So ``--p`` instead of ``--plots``
          also works, while ``--r`` does not, because it could mean ``--run`` as well as
          ``--results``. 


