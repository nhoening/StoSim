.. _remote_example:

Running simulations on remote computers
========================================

Summary
-------
You can let one or more remote servers handle the workload. Nicessa will try to split the work,
give each server some of it and fetch the results from them later.
We'll reuse our example from :ref:`subex_example` to show how this works.
Commands we will use here are ``--run``, ``--check`` and ``--results``

We can turn on remote mode in the main configuration (``nicessa.conf``) like this::

    local: 0


An example session
------------------
See the session below for a quick visualisation how you could work with it.
I configured two servers in the remote.conf file, one at work, and a server I pay for myself. 
The session  shows how I run the example (starting it on the remote hosts), then check if 
they're finished and once all their CPUs are done, get results and plot them:: 

    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa . --run
    ********************************************************************************
    Running simulation Subsimulation Example
    ********************************************************************************

    [Nicessa] Running code on ssh.cwi.nl
    [Nicessa] Running code on nicolashoening.de
    [Nicessa] deployed simulation on 2 host(s)
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa . --check
    [Nicessa] Checking hosts:  ssh.cwi.nl (host 1)   nicolashoening.de (host 2)  
    [Nicessa] Finished cpus:
     ssh.cwi.nl  :  []
     nicolashoening.de:     []
    [Nicessa] Still running cpus:
     ssh.cwi.nl  :  [1, 2]
     nicolashoening.de:     [1]
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa . --check
    [Nicessa] Checking hosts:  ssh.cwi.nl (host 1)   nicolashoening.de (host 2)  
    [Nicessa] Finished cpus:
     ssh.cwi.nl  :  [1, 2]
     nicolashoening.de:     []
    [Nicessa] Still running cpus:
     ssh.cwi.nl  :  []
     nicolashoening.de:     [1]
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa . --check
    [Nicessa] Checking hosts:  ssh.cwi.nl (host 1)   nicolashoening.de (host 2)  
    [Nicessa] Finished cpus:
     ssh.cwi.nl  :  [1, 2]
     nicolashoening.de:     [1]
    [Nicessa] Still running cpus:
     ssh.cwi.nl  :  []
     nicolashoening.de:     []
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa . --results --plots
    ********************************************************************************
    [Nicessa] getting results ... 
    [Nicessa] This may take a while, depending on your simulation. I'll tell you when I got everything from a host.
    [Nicessa] copying data from ssh.cwi.nl ...  done.
    [Nicessa] copying data from nicolashoening.de ...  done.
    _ [Nicessa] Got all results.
    ********************************************************************************


    ********************************************************************************
    [Nicessa] creating plots ...
    ********************************************************************************

    [Nicessa] Preparing ./plots/simulation1_cooperative.pdf:  learners-minority  learners-majority  learners_all 
    [Nicessa] Plotting ./plots/simulation1_cooperative.pdf

    [Nicessa] Preparing ./plots/simulation1_non-cooperative.pdf:  learners-minority  learners-majority  learners-all 
    [Nicessa] Plotting ./plots/simulation1_non-cooperative.pdf

    [Nicessa] Preparing ./plots/simulation1_payoff.pdf:  non-learners_in_coop  learners_in_coop  non-learners_in_non-coop  learners_in_non-coop 
    [Nicessa] Plotting ./plots/simulation1_payoff.pdf

    [Nicessa] Preparing ./plots/simulation2_cooperative.pdf:  learners-minority  learners-majority  learners_all 
    [Nicessa] Plotting ./plots/simulation2_cooperative.pdf

    [Nicessa] Preparing ./plots/simulation2_non-cooperative.pdf:  learners-minority  learners-majority  learners-all 
    [Nicessa] Plotting ./plots/simulation2_non-cooperative.pdf

    [Nicessa] Preparing ./plots/simulation2_payoff.pdf:  non-learners_in_coop  learners_in_coop  non-learners_in_non-coop  learners_in_non-coop 
    [Nicessa] Plotting ./plots/simulation2_payoff.pdf


The remopte.conf file
---------------------
If you have set ``local: 0``, you'll need to extend the configuration with 
some server credentials in a separate file. 
Nicessa will look for a file called `remote.conf <http://www.assembla.com/code/nicessa/subversion/nodes/trunk/examples/subsim/remote.conf>`_ with server credentials
and some other things. Here is an example (go to :ref:`remote_reference` for a full reference on the settings):

.. literalinclude:: ../../examples/subsim/remote.conf


Nicessa will transfer all the files to the servers and start background sreens on them, running a portion of the
workload (it only makes sense to have several servers when your simulation has multiple settings). 

If you did not use the ``--run`` command, then Nicessa checks
each server periodically if they are done. If they all are, 
it fetches the results. Then, plots are made locally, like usual. 


.. note:: The ``cpus``-setting gives you the opportunity to balance the workloads better.
          This makes sense if some of your servers have more CPUs than the others 
          (or you want to keep a CPU free on your own or your colleagues computer). 
          If all your servers have the same amount of CPUs, better leave it all at ``1``.
        
.. note:: When running remote simulations, make sure that the servers are known 
          in your .ssh/known_hosts file. I always connect to the servers once per 
          manual ssh login, where ssh asks me if I want to add that server to that file.

.. note:: By using ssh, your passwords will not be sent over the network in
          clear. However, I know it's not the best practice to keep passwords
          around in a file. I plan to incorporate the option for the systems
          keychain to get involved or at least to be prompted for the passwords
          rather than writing them down somewhere.

