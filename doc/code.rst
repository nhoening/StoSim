===================
stosim
===================

.. automodule:: stosim
    :members:

===================
sim
===================
Assisting code to support other code and prepare simulations

.. automodule:: stosim.sim.commands
    :members:
.. automodule:: stosim.sim.job_creator
    :members:
.. automodule:: stosim.sim.utils 
    :members:

===================
analysis
===================
Code used to analyse results: Plotting and T-testing.
The general workflow for an analysis:
We collect values from the whole data set, be it whole files which are
averaged or just selected values from files. The one result file will be
plotted or is input to a T-Test.

.. automodule:: stosim.analysis.harvester 
    :members:
.. automodule:: stosim.analysis.compressor 
    :members:
.. automodule:: stosim.analysis.plotter
    :members:
.. automodule:: stosim.analysis.tester
    :members:


