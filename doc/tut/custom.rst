=================================
Customising the analysis workflow
=================================

While the configuration of the execution workflow is completely 
straight-forward, the analysis workflow is a bit more complicated.

For its usage of Gnuplot and Gnu R, it automatically writes scripts
- which you, the user, might want a little different. Also, the refinement
step (selecting values out of filed to plot) can be configured.

Here are a few short tips on how to customise certain things of the analysis:


Custom selectors
-----------------

StoSim lets you select some values from the columns you want to analyse, e.g. 
the maximum value or simply the last one.
You can also write a custom selector and tell StoSim to use it.

.. warning:: Custom selectors are not implemented yet, 
             `but high on the TODO-list <http://www.assembla.com/space/stosim/tickets/23-custom-selectors>`_!


Custom plots
--------------

The possibilities of plot-making in StoSim are pretty interesting,
but of course one can do a lot more with Gnuplot. It is easy to link your
own Gnuplot script into the workflow.

There is an additional configuration setting per figure, called 
``custom-script``. Put here the path to your custom script, relative to the 
simulation folder (that is the first argument to StoSim), e.g.::

    [figure1]
    name: my_custom_plot
    y-range: [0:50]
    custom-script: my_scripts/figure1.gnu
    plot1: _name:fig1_plot1, _ycol:2, _type:line

.. note:: Graphical settings like ``y-range`` will not have any effect if
          you use a custom script.

.. note:: The plot<i> directives are helping you gather data, so you'll
          need one for every set of data you want to plot. 

Your script can make use of the work StoSim has done on selecting files,
columns and selected values in them. For each plot, your script can access 
these in a file called ``all.dat``, to be found in a directory named after
the ``_name`` attribute of the plot.

As a reference, here is a Gnuplot file that StoSim creates itself to make line
plots (from the tutorial :ref:`sub_example`):

.. literalinclude:: example.gnu

.. note:: You can see StoSims own Gnuplot script and all the data files it 
          creates for the analysis by simply adding ``-k`` to the call 
          (e.g. ``./stosim . --plots -k``). 
          This will keep StoSim from deleting its temporary files.
          There should now be a directory called ``tmp_plotter``, where you'll
          find a file called ``plot.gnu`` and a directory with collected
          data for the last generated plot. That might be a good starting point.


Custom tests
--------------
It is also possible to link custom Gnu R scripts into the analysis
workflow. It works exactly like in the plotting case above.
You add a ``custom-script`` setting to your test-description. Like so::

    [ttest1]
    name: condition1_yes_vs_no
    custom-script: my_scripts/ttest1.r
    set1: _name:yes, _col:2, condition1:yes
    set2: _name:no, _col:2, condition1:no

Each dataset will be in a file called ``[set-name].dat``, so in this example,
you can expect ``yes.dat`` and ``no.dat``. 
The Gnu R scripts StoSim uses are pretty trivial, but here is an example
nonetheless:
    
.. literalinclude:: example.r

.. note:: The ``-k`` option described above also works with tests. The
          directory to look in is called ``tmp_tester``.
