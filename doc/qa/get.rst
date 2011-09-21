.. _get:

How to get and install Nicessa
===============================

I develop nicessa in a `git <http://git-scm.com>`_ repository and do not make stable versions available (this will come soon).
You can simply download the latest version as `a zip-file <https://github.com/nhoening/Nicessa/zipball/master>`_. Unpack that, and you
are ready to go. Alternatively, you can get the code by using `git`, by typing ``git clone git@github.com:nhoening/Nicessa.git`` (git should be installed on
most unix systems these days, otherwise you have to install that first). This downloads the code and has the advantage that you can always update to the very latest
version by going in that new "Nicessa"-directory this created and typing ``git pull``.

You do not need to install Nicessa (but take care of the :ref:`depend`). All you need to use it is call ``nicessa.py``, which lies in the main folder.
However, my projects are always located somewhere else, so to make my life easier I use to make a shortcut 
to ``nicessa.py`` in my ``~/.bashrc`` file (or ``~/.profile`` on Mac): 
    
    ``alias nicessa='python </your/system/path/to/>/Nicessa/nicessa.py'``

so that on any command line, I can just type ``nicessa`` to start it, whereever I am.

