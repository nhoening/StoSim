#!/usr/bin/python

'''
starter
=========

Start jobs for configurations.
You can start a whole preconfigured batch, which then starts jobs for each single configuration.

This module is used locally by experiment.py.
Remotely, it is called via command line.
'''

import os
import os.path as osp
import sys
from subprocess import Popen
from socket import gethostname
import random
from ConfigParser import ConfigParser


def batch(expfolder, server, cpu):
    '''
    Make runs for each section in the main config file for this server and cpu
    (which itself just points to actual config files we created during setup)

    :param string expfolder: relative path to expfolder
    :param int server: index of server this batch is meant to run on
    :param int cpu: index of cpu this batch is meant to run on
    '''
    conf = ConfigParser()
    conf.read(osp.join(expfolder, "conf", str(server), str(cpu), "main.conf"))

    sections = [sec for sec in conf.sections() if not sec == 'seeds']

    print '*' * 80
    print '[Nicessa] Running jobs on cpu %i of server %s' % (cpu, gethostname())

    for section in sections:
        print;
        print "[Nicessa] Processing %d/%d \n(section %s)" % (sections.index(section)+1, len(sections), section)
        single(section, expfolder, conf, conf.get(section, 'config_file'))
    print
    print '*' * 80


def single(section, expfolder, uber_conf, config_file):
    '''
    Start runs for an individual configuration.
    Look up the right seed if seeds are configured.

    :param string section: section name - this is the name the data folder gets
    :param string expfolder: relative path to expfolder
    :param CinfigParser uber_conf: the main experiment configuration
    :param string config_file: name of the config file for this run
    '''
    conf = ConfigParser()
    conf.read('%s' % config_file)
    data_dirname = "%s/data" % (expfolder)
    section_dirname = "%s/%s" % (data_dirname, section)

    # make sure data section dir exists + copy actual config file there
    if not osp.exists(section_dirname):
        os.makedirs(section_dirname)
    Popen('cp %s %s' % (config_file, section_dirname), shell=True).wait()

    start_run = 1
    if conf.has_option('control', 'start_run'):
        start_run = conf.getint('control', 'start_run')

    for run in xrange(start_run, conf.getint('control','runs') + start_run, 1):
        print ".",
        sys.stdout.flush()

        seed = ''
        if uber_conf.has_section('seeds'):
            try:
                seed = uber_conf.get('seeds', str(run))
            except Exception, e:
                print "[Nicessa] There is no seed specified for run %d" % run
        else:
            random.seed()

        logfile = "%s/log%d.csv" % (section_dirname, run)
        csv = open(logfile, 'w')
        csv.write("# Log for run %d in experiment %s \n" % (run, conf.get('meta', 'name')))
        csv.flush()
        csv.close()
        Popen("%s/%s %s %s %s" % (expfolder, conf.get('control', 'executable'), logfile, config_file, seed), shell=True).wait()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "usage: ./starter.py experiment_folder server_number cpu_number"
        sys.exit()
    batch(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
