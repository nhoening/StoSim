.. _get:

How to get and install Nicessa
=============================

I develop nicessa in a subversion repository and don't make stable versions available (maybe later). 
You get the latest version by typing ``svn co http://my-svn.assembla.com/svn/nicessa``  (subversion, or svn, should be installed on
most unix systems these days, otherwise you have to install that first). This downloads the repository and you can always update it by
going in that new "nicessa"-directory this created and type ``svn up``.

I also made a shortcut to the main executable of nicessa in my ~/.bashrc file: 
    
    ``alias nicessa='python </your/system/path/to/>/nicessa/trunk/experiment.py'``

so that on any command line, I can just type ``nicessa`` to start it.

