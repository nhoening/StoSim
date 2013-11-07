Welcome to StoSim's documentation!
====================================

StoSim is a light-weight framework for parameterised simulations. The researcher provides the simulation itself (written in the language of his/her choice), 
but the framework relieves him/her of many generalisable technical tasks in 

  * configuring the simulation
  * executing many runs
  * and analysing the results

StoSim should be easy to get started with: By only writing one configuration file, your simulation will be parameterised and distributed on several cpus in the network. Then, paper-ready plots as well as T-tests are being created (see :ref:`basic_example`). All your code needs to do to work with StoSim is to read a set of parameters from a config file and write its output into a file which StoSim provides.

.. image:: img/wrapping.png
    :align: center

But StoSim also needs to be very customisable. For instance, you can plug in your own scripts to analyze the results which StoSim generated and selected for you. In addition, you might want to run the simulation on a computation cluster you have access to (this is high on our TODO-list).  

StoSim is developed under an open-source MIT license at the CWI Amsterdam and written in Python (but the simulation can be written in any programming language). Find the `code at github <https://github.com/nhoening/stosim/>`_ (click `here <https://github.com/nhoening/stosim/zipball/master>`_ to grab the latest version as a zip-archive). It makes use of open-source industry standards like Gnuplot and Gnu R.
While it proves very useful for its current small userbase, there is still lots of things to do even better (see `the Ticket tracker <http://www.assembla.com/spaces/stosim/tickets>`_) and a lot of great ideas to go from here. Let me know if you have ideas or want to contribute.

Please contact `Nicolas Honing <nicolas@cwi.nl>`_ with any questions or problems.

There also is a `PDF version <StoSim.pdf>`_ of this documentation

******************
Narrative contents
******************

.. toctree::
    :maxdepth: 2

    qa/what.rst
    qa/which.rst
    qa/workflows.rst
    qa/get.rst
    qa/usage.rst
    qa/underthehood.rst
    qa/depend.rst


.. image:: img/stosim-workflows.png
    :align: center
..    :scale: 40%


***************
Tutorials
***************

.. toctree::

    tut/basic.rst
    tut/sub.rst
    tut/stochastic.rst
    tut/remote.rst
    tut/custom.rst

************************
Configuration reference
************************

.. toctree::

    reference.rst


******************
Code documentation
******************

There is a detailled documentation of all internal modules and functions:

.. toctree::

    code.rst

    
.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

