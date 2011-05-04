Welcome to Nicessa's documentation!
====================================

Nicessa stands for "**\ N**\ on-\ **i**\ ntrusive **c**\ ombinatorial **e**\ xecution of **s**\ tochastic **s**\ imulations and their **A**\ nalysis".

When running stochastic simulations, there is a recurring set of technical 
tasks: Parameter settings need to be recombined, log files need to be managed, and the results need to be
analysed graphically and statistically. In addition, the computational workload should be distributed over
several computers.

NICESSA is a light-weight, general-purpose simulation framework, which relieves the researcher of generalisable technical tasks in the execution and analysis workflows, while being non-intrusive with respect to the individual implementation of the simulation model. 

NICESSA is developed under an open-source MIT license at the CWI Amsterdam and written in Python (but the simulation can be written in any programming language). It makes use of open-source industry standards like Gnuplot and Gnu R.

Please contact `Nicolas Honing <nicolas@cwi.nl>`_ with any questions or problems.


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


.. image:: img/nicessa-workflows.png
    :align: center
    :scale: 90%


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

