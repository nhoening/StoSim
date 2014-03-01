.. _get:

How to get and install StoSim
===============================

StoSim lives on the `Python Package index <http://www.pypi.org>`_, so you can install it with

    ``pip install stosim``

Then you should have the ``stosim`` command available and you are done.

To upgrade to a new version, you would do:

    ``pip install --upgrade stosim``

If you don't have the necessary privileges, you might add the --user option, e.g.:

    ``pip install stosim --user``

For the --user option to work, ``~/.local/bin`` should be in your PATH (if it is not, do ``export PATH=~/.local/bin:$PATH``).


Other options
-------------

If you don't have pip, maybe you can do

    ``easy_install pip``

or

    ``easy_install --user pip``

You could also get the source directly, of course. 
I develop StoSim in a `git <http://git-scm.com>`_ repository.
You can simply download the latest version as `a zip-file <https://github.com/nhoening/stosim/zipball/master>`_. Unpack that, and you
are ready to go. Alternatively, you can get the code by using `git`, by typing ``git clone git@github.com:nhoening/stosim.git`` (git should be installed on most Unix systems these days, otherwise you have to install that first). This downloads the code and has the advantage that you can always update to the very latest version by going in that new "stosim"-directory this created and typing ``git pull``.

Do this to install the source:

    ``cd stosim; python setup.py develop``

For completeness: You do not need to install StoSim if you get the source (but take care of the :ref:`depend`).
All you need to use it is call ``stosim.py``, which lies in the main folder.
However, my projects are always located somewhere else, so to make my life easier I use to make a shortcut 
to ``stosim.py`` in my ``~/.bashrc`` file (or ``~/.profile`` on Mac): 
    
    ``alias stosim='python </your/system/path/to/>/stosim/stosim.py'``

so that on any command line, I can just type ``stosim`` to start it, whereever I am.


Run tests
-------------

Go to StoSim's main directory.

    ``python setup.py test``

If you have tox installed (which is awesome):

    ``tox``

or

    ``tox -e coverage``

The first tox command runs tests, possibly for several versions of Python. 
The second shows you coverage of the tests on StoSim's code.
