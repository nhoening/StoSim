.. _stochastic_example:

Using stochastic features
=============================

Summary
-------
In this example, we revisit the example from :ref:`sub_example`, only now we look
at all the features StoSim offers for stochastic simulations.
We look at error-bars in line plots, fixing a seed for each run for repeatability, 
performing T-Tests and adding more runs to the database (as well as checking 
what is in the database).


Error-bars
----------
First, let's add error-bars to the line graphs, so we can see how
much variance is in the data. There is two configuration settings
that are of interest for this:

.. literalinclude:: ../../examples/stochastic/stosim.conf
    :lines: 37-39


First, we say that we indeed want to see error-bars and then we
say how far apart, horizontally, they should be plotted.
Here is one plot from the second subsimulation,
to show you what it looks like:

.. figure:: ../img/PD_sim2_errorbars.png
    :scale: 60%

    Errorbar plot from sub-simulation example

We see that there is not much variance anywhere, except maybe when
all agents are learners.

.. note:: This feature is restricted to line plots. It doesn't make a lot of
          sense in a scatter plot.


Seeds
--------
You can provide a seed for every run of your
simulation, for repeatability of your randomised results.
In this example, we do five runs, so we provide a distinct
seed for every one. Here are the first five:

.. literalinclude:: ../../examples/stochastic/stosim.conf
    :lines: 25-31

The seed is written into the job configuration which is passed to your executable. Have a look in 
`the executable for this simulation
<https://github.com/nhoening/StoSim/raw/master/examples/stochastic/main.py>`_
(near the bottom) to see how it uses the gets the seed and seeds the randomizer with it.


.. note:: The length of a seed is up to you. Your program needs to handle it. 
          For instance, it might matter if you store it in an integer or a long variable.


T-tests
--------
A T-Test is configured much like a Figure, only it is simpler.
In the first sub-simulation, we saw that payoff was bigger in the 
cooperative scenario. Let's put that to a T-Test:

.. literalinclude:: ../../examples/stochastic/stosim.conf
    :lines: 41-44

Here is the output of the Gnu R T-Test, which confirms our hypothesis
that the difference is significant::

  nic@fidel:/media/data/projects/stosim/trunk/examples/stochastic$ stosim --ttests

  ********************************************************************************
  [StoSim] Running T-tests ...
  ********************************************************************************

  Test payoff_coop_vs_noncoop:
  > coop <- read.table('coop.dat')
  > noncoop <- read.table('noncoop.dat')
  > t.test(coop,noncoop)
   
	  Welch Two Sample t-test
  
  data:  coop and noncoop 
  t = 61.9744, df = 3477.865, p-value < 2.2e-16
  alternative hypothesis: true difference in means is not equal to 0 
  95 percent confidence interval:
  0.6861417 0.7309741 
  sample estimates:
  mean of x mean of y 
  2.406372  1.697814 


Adding more runs
----------------
Sometimes you might want to add a couple of runs, to add statistical
weight to the results. That is quite easy in StoSim. The following session 
shows how to use the ``--list`` and ``--more`` commands to see how
many runs you have and add more. Here, I had only made runs for simulation 2
(``stosim --simulations=sim2``) and I add another 5 runs (note that
I now have 10 runs for some of the configurations, so I'd better also
have 10 seeds)::

    nic@fidel:/media/data/projects/stosim/trunk/examples/stochastic$ stosim --list
    [StoSim] The configurations and number of runs made so far:

    sim1
    No runs found for simulation sim1

    sim2
    --------------------------------------------------------------------------------------------------------
    |   mean_coop  |   n  |   epochs  |   pd_t  |   ratio_learning  |   pd_p  |   pd_s  |   pd_r  | | runs |
    --------------------------------------------------------------------------------------------------------
    |   0.2        |   100|   200     |   5     |   0.25            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.8        |   100|   200     |   5     |   0.25            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.8        |   100|   200     |   5     |   0.75            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.2        |   100|   200     |   5     |   0.75            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.2        |   100|   200     |   5     |   1               |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.8        |   100|   200     |   5     |   1               |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    nic@fidel:/media/data/projects/stosim/trunk/examples/stochastic$ stosim --more
    [StoSim] Let's make 5 more runs! Please tell me on which configurations.
    Enter any parameter values you want to narrow down to, nothing otherwise.
    ratio_learning ? (out of [0.25,0.75,1])
    1
    mean_coop ? (out of [0.2,0.8])

    No restriction chosen.
    You selected: {'ratio_learning': ['1']}. Do this? [Y|n]
    (Remember that configuration and code should still be the same!)

    ********************************************************************************
    Running simulation The stochastic-features example
    ********************************************************************************

    ********************************************************************************
    [StoSim] Running jobs on cpu 1 of server fidel

    [StoSim] Processing 1/4 
    (section sim1_mean_coop0.2_n100_epochs200_pd_t5_ratio_learning1_pd_p1_pd_s0_pd_r3)
    . . . . .
    [StoSim] Processing 2/4 
    (section sim2_mean_coop0.2_n100_epochs200_pd_t5_ratio_learning1_pd_p1_pd_s1_pd_r5)
    . . . . .
    [StoSim] Processing 3/4 
    (section sim1_mean_coop0.8_n100_epochs200_pd_t5_ratio_learning1_pd_p1_pd_s0_pd_r3)
    . . . . .
    [StoSim] Processing 4/4 
    (section sim2_mean_coop0.8_n100_epochs200_pd_t5_ratio_learning1_pd_p1_pd_s1_pd_r5)
    . . . . .
    ********************************************************************************
    nic@fidel:/media/data/projects/stosim/trunk/examples/stochastic$ stosim --list
    [StoSim] The configurations and number of runs made so far:

    sim1
    --------------------------------------------------------------------------------------------------------
    |   mean_coop  |   n  |   epochs  |   pd_t  |   ratio_learning  |   pd_p  |   pd_s  |   pd_r  | | runs |
    --------------------------------------------------------------------------------------------------------
    |   0.2        |   100|   200     |   5     |   1               |   1     |   0     |   3     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.8        |   100|   200     |   5     |   1               |   1     |   0     |   3     | |    5 |
    --------------------------------------------------------------------------------------------------------
    sim2
    --------------------------------------------------------------------------------------------------------
    |   mean_coop  |   n  |   epochs  |   pd_t  |   ratio_learning  |   pd_p  |   pd_s  |   pd_r  | | runs |
    --------------------------------------------------------------------------------------------------------
    |   0.2        |   100|   200     |   5     |   0.25            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.8        |   100|   200     |   5     |   0.25            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.8        |   100|   200     |   5     |   0.75            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.2        |   100|   200     |   5     |   0.75            |   1     |   1     |   5     | |    5 |
    --------------------------------------------------------------------------------------------------------
    |   0.2        |   100|   200     |   5     |   1               |   1     |   1     |   5     | |   10 |
    --------------------------------------------------------------------------------------------------------
    |   0.8        |   100|   200     |   5     |   1               |   1     |   1     |   5     | |   10 |
    --------------------------------------------------------------------------------------------------------


