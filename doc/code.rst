.. automodule:: experiment 
    :members:

===================
sim
===================
Assisting code

.. automodule:: sim.setup
    :members:
.. automodule:: sim.utils 
    :members:

===================
sim.net
===================
Code used to run simulations, also on remote computers

.. automodule:: sim.net.remote 
    :members:
.. automodule:: sim.net.starter 
    :members:
.. automodule:: sim.net.screener 
    :members:


===================
analysis
===================
Code used to analyse results: Plotting and T-testing.
The general workflow for an analysis:
We collect values from the whole data set, be it whole files which are
averaged or just selected values from files. The one result file will be
plotted or is input to a T-Test.

.. automodule:: analysis.harvester 
    :members:
.. automodule:: analysis.compressor 
    :members:
.. automodule:: analysis.plotter
    :members:
.. automodule:: analysis.tester
    :members:


