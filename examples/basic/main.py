#!/usr/bin/python
"""
Example stosim simulation runner,
showing very basic usage by conducting random walks

The only thing actually needed is a __main__ block (see bottom), so that this
script is callable from the command line.
The rest of this file shows how onfiguration files can be used and log files
be written. Pointers to both are supplied by StoSim.

Note that because StoSim calls this script in a system call
(like you would from a command line), this example could also be a Java file*.
The point is, your simulation doesn't have to be written in Python.
All it should do is read a config file and write to a log file.

* which you would need to precompile, of course
"""
try:
    import configparser
except ImportError:
    import ConfigParser as configparser  # for py2
import random
import sys


if __name__ == '__main__':
    '''
    This gets called by stosim for each run, since the name of this script
    was named in stosim.conf - StoSim will pass to it:
    (1) the name of the log file
    (2) the name of the conf file
    which are specific to this run.
    '''

    # open the conf file for this run with the standard Python way
    conf = configparser.ConfigParser()
    conf.read(sys.argv[1])
    # open the log StoSim says we should write to when we run this job
    log = open(conf.get('stosim', 'logfile'), 'w')

    # The parameters from the conf for this run can be accessed like this
    max_step = conf.getint('params', 'steps')

    val = 0
    random.seed()
    for step in range(1, max_step+1):
        dbl = random.random()
        if dbl > .5:
            val += 1
        else:
            val -= 1
        # we write two columns per row: step and value
        log.write("%d\t%d\n" % (step, val))
    log.flush()
    log.close()
