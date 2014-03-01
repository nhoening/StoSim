.. _which:

Which kind of simulations would I run with StoSim?
=====================================================

Four short points
------------------

Basically, almost any simulation can be run with StoSim. Let me explain the workings of StoSim by making four short points:

  * You need to **have an executable**.
        By this, I mean any program or script that can be executed to run your simulation.
        StoSim is non-intrusive, in the sense that your executable will run totally independent - StoSim will only hand it 
        settings and the name of a log file.
        Basically, you could have an executable (e.g. a JAVA - script) be run by StoSim 
        and care for nothing else, but of course it makes more sense if you mae use of the features below, as well.
  * You should **write log files** (but who doesn't?).
        StoSim hands your executable the filename of an (empty) log file. 
        Write values in it, then you can make use of StoSim's analysis tools, e.g. automated plotting (see below)!
  * You can **use different parameter settings**.
        It's easy to set different values for parameters in the conf files.
        Stosim will pass the filename of a prepared configuration file to your executable. The cool thing: If you want to try out three different values for
        a parameter, just write ``my_parameter: val_1,val_2,val_3``. StoSim internally makes three different configuration files
        out of this and calls your code three times, once with each setting. Nowhere else in your code do you need to care
        that you are trying out different settings (If you also have ``my_other_parameter: val_a,val_b,val_c``, then you'll
        have 9 combinations and your code gets called 9 times).
  * You can **analyse**.
        Everyone wants to do something with the data their simulation accumulated. And everyone has their custom
        scripts for that that need to be adapted every time. StoSim wants to be
        an analysis tool and do a good job for most of the use cases. It supports plotting and T-testing
        (see :ref:`using_plotting` for more).


Stochastic simulations
------------------------

StoSim has been tailored to work very well with stochastic simulations:

  * You can say **how many runs** you want to have done and even add more runs to the data you already collected (even only for specific configurations). 
  * You can also specify a list of **seeds**, so that the n-th run always uses the n-th key (nice for reproducability). 
  * Plots can have **errorbars**
  * You can request **T-tests** to be made, in order to look at statistical significance.

To make your simulation actually stochastic in the first place, however, is your job. StoSim just runs whatever code you tell it to run.
