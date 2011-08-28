.. _remote_example:

========================================
Running simulations on remote computers
========================================

Summary
-------
You can let one or more remote computers (hosts) handle the workload. Nicessa will try to split the work,
give each server some of it and fetch the results from them later.

Nicessa will transfer all the files to the hosts and start background screens on them, running a portion of the
workload (it only makes sense to have several hosts when your simulation has multiple settings). 

You can turn on remote mode in the main configuration (``nicessa.conf``) like this::

    local: 0

We'll now reuse our example from :ref:`subex_example` to show how this works.
Commands we will use here are ``--run``, ``--check``, ``--results`` and ``--plots``.



An example session
------------------
See the session below for a quick visualisation how you could work with it.
I configured two hosts in the remote.conf file, one at work, and a hosts I pay for myself. 
The session  shows how I run the example (starting it on the remote hosts), then check if 
they're finished and once all their CPUs are done, get results and plot them:: 

    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa --run
    ********************************************************************************
    Running simulation Subsimulation Example
    ********************************************************************************
    [Nicessa] Preparing hosts ...
    [Nicessa] Running code on ssh.cwi.nl
    [Nicessa] Running code on nicolashoening.de
    [Nicessa] deployed simulation on 2 host(s)
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa --check
    [Nicessa] Checking hosts:  ssh.cwi.nl (host 1)   nicolashoening.de (host 2)  
    [Nicessa] Finished cpus:
     ssh.cwi.nl  :  []
     nicolashoening.de:     []
    [Nicessa] Still running cpus:
     ssh.cwi.nl  :  [1, 2]
     nicolashoening.de:     [1]
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa --check
    [Nicessa] Checking hosts:  ssh.cwi.nl (host 1)   nicolashoening.de (host 2)  
    [Nicessa] Finished cpus:
     ssh.cwi.nl  :  [1, 2]
     nicolashoening.de:     []
    [Nicessa] Still running cpus:
     ssh.cwi.nl  :  []
     nicolashoening.de:     [1]
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa --check
    [Nicessa] Checking hosts:  ssh.cwi.nl (host 1)   nicolashoening.de (host 2)  
    [Nicessa] Finished cpus:
     ssh.cwi.nl  :  [1, 2]
     nicolashoening.de:     [1]
    [Nicessa] Still running cpus:
     ssh.cwi.nl  :  []
     nicolashoening.de:     []
    ~/Documents/nicessa/trunk/examples/subsim nic$ nicessa --results --plots
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

If you do not use the ``--run`` command, then Nicessa aassumes a default workflow: It checks
each host periodically if they are done. If they all are, it fetches the results. Then, plots are made locally, like usual. 

In the above example, I wanted more control over the flow, so I used the ``--check``, ``--results`` and ``--plots`` commands 
in multiple calls.


Authentication
------------------
In the above example, Nicessa did not ask me to authenticate on the hosts. Normally it would, but since that is annoying after a while, it is a good idea
to make use of the powers of SSH setup to enable paswordless logon.
`There are many ways to ease your life <http://blogs.perl.org/users/smylers/2011/08/ssh-productivity-tips.html>`_:
You can set up RSA keys to connect with the hosts, use the ``ControlPersist`` option in the SSH config file to keep connections alive 
(only OpenSSH >= 5.6) or simply have one SSH connection open somewhere and let SSH share it.

Note that Nicessa could theoretically offer to store the passwords for hosts in the ``remote.conf`` file, but that is not a safe procedure by any means.
Many smart people thought hard about the best ways to do it and we should use what they came up with.

When running remote simulations, make sure that the hosts are known 
in your ~/.ssh/known_hosts file. Simply connect to the servers once per 
manual SSH login, where SSH asks you if you want to add that server as a known host.


The remote.conf file
---------------------
If you have set ``local: 0``, you'll need to extend the configuration with 
some information about the hosts in a separate file. 
Nicessa will look for a file called `remote.conf <http://www.assembla.com/code/nicessa/subversion/nodes/trunk/examples/subsim/remote.conf>`_ with information about hosts
and some other things. Here is an example (go to :ref:`remote_reference` for a full reference on the settings):

.. literalinclude:: ../../examples/subsim/remote.conf

 

.. note:: The ``cpus``-setting gives you the opportunity to balance the workloads better.
          This makes sense if some of your servers have more CPUs than the others 
          (or you want to keep a CPU free on your own or your colleagues computer). 

.. note:: To find out how many cores (cpus) a computer has, you might want to use the UNIX-command ``mpstat -P ALL``, which shows you current activity on all cores.
        

