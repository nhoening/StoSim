========================
Configuration Reference
========================

This reference will list all configuration settings that are
available to you, ordered by section where they should be placed.
It will not explain them in context. For that, consult the
examples, mostly the :ref:`basic_example`.

.. note:: Mandatory options are marked with (**M**).


.. _main_reference:

Main configuration
------------------------
These are the settings you can make in ``stosim.conf`` or
in subsimulation configurations (see :ref:`sub_example`).

meta
^^^^^^
General Description

:name:
    Name of the exeriment

:maintainer:
    The person who is responsible for this simulation


control
^^^^^^^^
:executable:
    Which script to call for each run (**M**)
    This should be just the name of the script and nothing else. StoSim will
    assume it is accessible relative to the simulation folder (per default in 
    '.'). If your code has to be called in a more difficult way (e.g. "java -jar ..."),
    simply make a simple bash script to contain that and name the script as your executable.
:runs:
    How often the same configuration should be run, defaults to 1
:scheduler:
    The job scheduler to use. Either 'fjd' (default - uses locally available CPUs, see
    https://pypi.python.org/pypi/fjd) or 'pbs', the most-used cluster environment.
:fjd-interval:
    If you are using the fjd scheduler, you can tell the workers how often to
    check for new jobs. The default is a fraction of a second, so if you have long jobs,
    you could increase the interval and thus relieve your CPUs from all the queue
    checking.
:pbs-jobtime:
    If you are using a PBS scheduler (cluster), you should tell the cluster scheduler
    the maximal time you expect a job to last, which will enable it to allocate
    nodes efficiently. The format is HH:MM:SS. The default is 00:05:00, so for
    long jobs, you probably want to increase this.
:delimiter:
    the delimiter your simulation uses to separate values in its log files,
    defaults to a comma (,) if you leave this setting away

params
^^^^^^^
Parameters of your simulation (whichever you need)
if you want more than one setting for a parameter, give a comma-separated list


seeds
^^^^^^^
A list of seeds to use per run, for repeatability.
This section is optional.

:<i>:
    The seed for run number <i>

simulations
^^^^^^^^^^^^
Use this if you separate simulations into separate sub-configs
(see :ref:`sub_example`).
This section is optional.

:configs:
    A comma-separated list of config-file names (without the .conf file ending) e.g. sim1,sim2


.. _plot_reference:

plots
^^^^^^

plot-settings
*************
General settings for all plots. This section is optional.

:use-colors:
    Whether to be black & white (0) or in color (1 - default)
:line-width:
    Line width in pt, default 6  
:font-size:
    Font-size, default 22
:infobox-pos:
    Where the infobox should go, e.g. 'bottom left',
    defaults to 'top left' when given empty
:use-y-errorbars: 
    A 1 if errorbars should be shown, 0 otherwise (default)
:errorbar-every:
    Show an errorbar every x steps, defaults to 10
:use-tex:
    whether to use enhanced mode, which interpretes
    tex-like encoding (e.g. subscript, math, greek symbols), defaults to False
:params:
    You can give a list of parameter settings here (just as you normally do 
    in the plot-options for each figure, see below), which all plots on all figures should adhere to. This can be very 
    convenient if you need to check how several figures change given the difference in one parameter setting.

figure<i>
**********
Settings for Figure <i> (start counting i at 1). All settings from plot-settings can be overwritten here.
In addition, you can specify:

:name:
    Name of the Figure (**M**)
:xcol:
    Index of the x-column in the data (**M**)
:x-label:
    Label on X-axis
:y-label:
    Label on Y-axis
:x-range:
    Value range of X-axis (in line plots, gnuplot choses this pretty good on its
    own)
:y-range:
    The range of values for y axis, defaults to '[0:10]'
:custom-script:
    Path (relative from simulation folder) to a custom gnuplot script that
    should be used instead of the automatically generated one.

plot<j>
*******
This is not a section, but an option in a Figure. You need at least one to 
describe data to plot (start counting j at 1).
You pass it a comma-separated list of settings (setting:value). 
First, these are the system-specific settings you can/need to set:

:_name:
    Name of the plot (**M**)
:_ycol:
    Index of the y-column in the logfiles you are interested in - start counting with 1  (**M**)
:_type:
    Type of plot, 'line' or 'scatter' (**M**)
:_select:
    Use this to select certain values from the y-column.
    One out of ['all', 'last', 'max_x', 'max_y', 'min_x', 'min_y'],
    defaults to 'all'.

In addition, you can narrow down your data set for this plot by giving some
settings for your parameters (e.g. ``param_1:value_a``).

StoSim has to parse the ``plot<j>`` string, so if you really want to use ``,`` or ``:`` in a name or value, escape it with ``\``.  


tests
^^^^^^^

test<i>
********
Settings for T-Test <i> (start counting i at 1)

:name:
    Name of the Test (**M**)
:custom-script:
    Path (relative from simulation folder) to a custom gnuplot script that
    should be used instead of the automatically generated one.

set<j>
********
This is not a section, but an option in a Test. You need at least one to 
describe data to test (for T-Tests: at least two) - start counting j at 1. 
You pass it a comma-separated list of settings (setting:value). 
First, these are the system-specific settings you can/need to set:

:_name:
    Name of the data set (**M**)
:_col:
    The column in the logfiles which you are interested in - start counting with 1 (**M**)
:_select:
    Use this to select certain values from the y-column.
    One out of ['all', 'last', 'max_x', 'max_y', 'min_x', 'min_y'] (**M**)

In addition, you can narrow down your data set for this test by specifying some parameter settings.

StoSim has to parse the ``set<j>`` string, so if you really want to use ``,`` or ``:`` in a name or value, escape it with ``\``.  


.. _remote_reference:

Remote computer configuration
-----------------------------

These settings would be in a file called ``remote.conf`` if you are using fjd
as scheduler (see above) and want to use other computers than your own.

host<i>
^^^^^^^^^^^
Settings for computer <i> (start counting i at 1)

:name:
    Hostname (**M**)
:workers:
    Number of cpus to be used on this server (**M**)
:nice:
    Level of niceness the jobs on this host should have (see Unix nice). Defaults to 9.

There is no password setting as it is not secure to write those down. To ease your life, `here are a couple tips <http://blogs.perl.org/users/smylers/2011/08/ssh-productivity-tips.html>`_.
You can set up RSA keys to connect with the hosts, keep connections alive for several hours 
(only OpenSSH >= 5.6) or simply have one SSH connection open somewhere and let SSH share it.
