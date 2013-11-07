.. _remote_example:

========================================
Running simulations on remote computers
========================================

Summary
-------
You can let one or more remote computers (hosts) handle the workload. StoSim will split the work into jobs
and let the hosts do them when they are free.

There are two schedulers you can choose in the main configuration (``stosim.conf``) like this::

    scheduler: pbs

The default scheduler is `fjd <https://pypi.python.org/pypi/fjd>`_, which uses the CPUs on your local machine or the ones in 
your local network (if the all have access to a shared home directory). More on this below.

The other scheduler is `pbs <en.wikipedia.org/wiki/Portable_Batch_System>`_ which is a major job description standard for computational clusters.

We'll now reuse our example from :ref:`subex_example` to show how this works.


Authentication
------------------
In the above example, StoSim did not ask me to authenticate on the hosts. 
If you use fjd to involve machines in your local network, StoSim would need to ask you for your credentials on these hosts very often.
This is annoying after a while, so it is a good idea to make use of the powers of SSH setup to enable paswordless authentication.
`There are many ways to ease your life <http://blogs.perl.org/users/smylers/2011/08/ssh-productivity-tips.html>`_:
You can set up RSA keys to connect with the hosts, use the ``ControlPersist`` option in the SSH config file to keep connections alive 
(only OpenSSH >= 5.6) or simply have one SSH connection open somewhere and let SSH share it.

Note that StoSim could theoretically offer to store the passwords for hosts in the ``remote.conf`` file, but that is not a safe procedure by any means. Many smart people thought hard about the best ways to do it and we should use what they came up with.

When running remote simulations, make sure that the hosts are known 
in your ~/.ssh/known_hosts file. Simply connect to the servers once per 
manual SSH login, where SSH asks you if you want to add that server as a known host.


The remote.conf file
---------------------
If you use fjd and want to involve computers in your local network, you'll need to extend the configuration with some information about the hosts in a separate file. 
StoSim will look for a file called `remote.conf <https://github.com/nhoening/StoSim/raw/master/examples/subsim/remote.conf.example>`_ with information about hosts. Here is an example (go to :ref:`remote_reference` for a full reference on the settings):

.. literalinclude:: ../../examples/subsim/remote.conf.example

You can rename ``examples/subsim/remote.conf.example`` to ``remote.conf`` and fill in some hosts in your network. When you run the ``subsim`` example, you should see it working.

.. note:: To find out how many cores (cpus) a computer has, you might want to use the UNIX-command ``mpstat -P ALL``, which shows you current activity on all cores.
        

