.. _remote_example:

Running simulations on remote computers
========================================

Summary
-------
You can let one or more remote servers handle the workload. Nicessa will try to split the work,
give each server some of it and fetch the results from them later.
We'll reuse our example from :ref:`subex_example` to show how this works.
Commands we will use here are ``--run``, ``--check`` and ``--results``

We can turn on remote mode in the main configuration (``experiment.conf``) like this::

    local: 0


An example session
------------------
See the session below for a quick visualisation how you could work with it: 
It shows how I run the example remotely, check if they're finished, get results and plot them. 




The servers.conf file
---------------------
If you have set ``local: 0``, you'll need to extend the configuration with 
some server credentials in a separate file. 
Nicessa will look for a file called `remote.conf <../../../examples/subexp/remote.conf>`_ with server credentials
and some other things. Here is an example (go to :ref:`remote_reference` for a full reference on the settings):

.. literalinclude:: ../../examples/subexp/remote.conf


Nicessa will transfer all the files to the servers and start background sreens on them, running a portion of the
workload (it only makes sense to have several servers when your experiment has multiple settings). 

If you did not use the ``--run`` command, then Nicessa checks
each server periodically if they are done. If they all are, 
it fetches the results. Then, plots are made locally, like usual. 


.. note:: The ``cpus``-setting gives you the opportunity to balance the workloadds better.
          This makes sense if some of your servers have more CPUs than the others 
          (or you want to keep a CPU free on your own or your colleagues computer). 
          If all your servers have the same amount of CPUs, better leave it all at ``1``.
        
.. note:: When running remote experiments, make sure that the servers are known 
          in your .ssh/known_hosts file. I always connect to the servers once per 
          manual ssh login, where ssh asks me if I want to add that server to that file.

.. note:: By using ssh, your passwords will not be sent over the network in
          clear. However, I know it's not the best practice to keep passwords
          around in a file. I plan to incorporate the option for the systems
          keychain to get involved or at least to be prompted for the passwords
          rather than writing them down somewhere.

