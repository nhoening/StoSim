#!/usr/bin/python

"""
experiment
==========

Utility functions to
  * run experiments (locally or on some -up to 4- remote hosts via ssh access),
  * get data from hosts
  * generate plots
  * run T-tests
  * list runs so far

The functions all expect the name of the experiment folder which should have an experiment.conf file in it.
An experiment folder will in the end contain the following dirs:

  * conf (configurations for batches of needed computations)
  * data (all log files)
  * plots (generated PDFs)

This module is careful with imports since it might be used in another context (on a remote host) and if
no remote support is needed, the user doesn't need paramiko
"""

import os
import os.path as osp
import sys
from shutil import rmtree
from ConfigParser import ConfigParser
from subprocess import Popen

from sim.net import starter


def run_experiment(expfolder):
    ''' The main function to start running experiments

        :param string expfolder: relative path to expfolder
    '''
    from sim import setup, utils

    print '*' * 80
    exp = utils.ensure_name(expfolder)
    print "Running experiment %s" % utils.get_pretty_experiment_name("%s/experiment.conf" % expfolder, exp)
    print '*' * 80
    print;

    if not osp.exists("%s/experiment.conf" % expfolder):
        print "[Nicessa] %s/experiment.conf does not exist!" % expfolder
        utils.usage()
        return 0

    if utils.is_remote(expfolder) or utils.cpus_per_host(expfolder)[1] > 1:
        from sim.net import remote
        remote.run_remotely(expfolder, utils.get_main_conf(expfolder))
    else:
        #for s in range(utils.num_hosts(expfolder)):
        #for cpu in range(utils.cpus_per_host(expfolder)[s]):
        starter.batch(expfolder, 1, 1)


def run_more(expfolder):
    """ let the user make more runs on current config, in addition to the given data

        :param string expfolder: relative path to expfolder
    """
    from sim import utils
    expfolder = expfolder.strip('/')
    conf = utils.get_main_conf(expfolder)

    print "[Nicessa] Let's make %d more runs! Please tell me on which configurations.\n" % conf.getint('control', 'runs') \
          + "Enter any parameter values you want to narrow down to, nothing otherwise."

    sel_params = {}
    for o in conf.options('params'):
        selected = False
        params = [p.strip() for p in conf.get('params', o).split(',')]
        if len(params) <= 1:
            continue # no need to narrow down
        while not selected:
            print "%s ? (out of [%s])" % (o, conf.get('params', o))
            choice = []
            for selection in raw_input().split(','):
                selected = True
                if selection == "":
                    pass
                elif selection in params:
                    choice.append(selection)
                else:
                    print "Sorry, %s is not a valid value." % selection
                    selected = False
        if len(choice) > 0:
            sel_params[o] = choice
        else:
            print "No restriction chosen."
    print "You selected: %s. Do this? [Y|n]\n(Remember that configuration and code should still be the same!)" % str(sel_params)
    if raw_input().lower() in ["", "y"]:
        _prepare(expfolder, limit_to=sel_params, more=True)
        run_experiment(expfolder)


def make_plots(expfolder):
    """ generate plots as specified in the experiment conf

        :param string expfolder: relative path to expfolder
    """
    from sim import utils
    from analysis import plotter

    expfolder = expfolder.strip('/')

    #if osp.exists("%s/plots" % expfolder):
    #   rmtree('%s/plots' % expfolder)
    if not osp.exists("%s/plots" % expfolder):
        os.mkdir('%s/plots' % expfolder)

    # tell about what we'll do if we have at least one plot
    relevant_confs = utils.get_relevant_confs(expfolder)
    for c in relevant_confs:
        if c.has_section("figure1"):
            print;
            print '*' * 80
            print "[Nicessa] creating plots ..."
            print '*' * 80
            print;
            break
    else:
        print "[Nicessa] No plots specified"

    # Describe all options first.
    # These might be set in plot-settings (in each experiment config) and per-figure
    general_options = {'use-colors':bool, 'use-tex':bool, 'line-width':int,\
                       'font-size':int, 'infobox-pos':str,\
                       'use-y-errorbars':bool, 'errorbar-every':int
                      }
    figure_specific_options = {
                       'name': str, 'xcol':int, 'x-range':str,\
                       'y-range':str, 'x-label': str, 'y-label': str,\
                       'custom-script':str
                      }
    figure_specific_options.update(general_options)

    def get_opt_val(conf, d, section, option, t):
        if conf.has_option(section, option):
            val = c.get(section, option).strip()
            if t is int:
                val = c.getint(section, option)
            if t is bool:
                val = c.getboolean(section, option)
            if t is float:
                val = c.getfloat(section, option)
            # config-options with '-' are nice, but not good parameter names
            d[option.replace('-', '_')] = val

    general_settings = {}
    c = ConfigParser(); c.read('%s/experiment.conf' % (expfolder))
    for o,t in general_options.iteritems():
        get_opt_val(c, general_settings, 'plot-settings', o, t)

    for c in relevant_confs:
        i = 1
        settings = general_settings.copy()
        # overwrite with plot-settings for this subexperiment
        for o, t in general_options.iteritems():
            get_opt_val(c, settings, 'plot-settings', o, t)

        while c.has_section("figure%i" % i):
            fig_settings = settings.copy()
            for o,t in figure_specific_options.iteritems():
                get_opt_val(c, fig_settings, 'figure%i' % i, o, t)

            plots = []
            j = 1
            while c.has_option("figure%i" % i, "plot%i" % j):
                d = utils.decode_search_from_confstr(
                        c.get('figure%i' % i, 'plot%i' % j),
                        exp=c.get('meta', 'name')
                    )
                # making sure all necessary plot attributes are there
                if d.has_key('_name') and d.has_key('_ycol') and d.has_key('_type'):
                    plots.append(d)
                else:
                    print '[NICESSA] Warning: Incomplete graph specification in Experiment %s - for plot %i in figure %i. '\
                          'Specify at least _name and _ycol.' % (c.get('meta', 'name'), j, i)
                j += 1
            plotter.plot(filepath='%s/data' % expfolder,\
                         outfile_name='%s/plots/%s.pdf' \
                            % (expfolder, fig_settings['name']),\
                         plots=plots,\
                         **fig_settings)
            i += 1


def run_ttests(expfolder):
    '''
    Make statistical t tests

    :param string expfolder: relative path to expfolder
    '''
    from analysis import harvester, tester
    relevant_confs = utils.get_relevant_confs(expfolder)

    # tell about what we'll do if we have at least one test
    for c in relevant_confs:
        if c.has_section("ttest1"):
            print;
            print '*' * 80
            print "[Nicessa] Running T-tests ..."
            print '*' * 80
            print;
            break
    else:
        print "[Nicessa] No T-tests specified"

    for c in relevant_confs:
        i = 1

        while c.has_section("ttest%i" % i):
            print "Test %s:" % c.get('ttest%i' % i,'name').strip('"')
            if not c.has_option("ttest%i" % i, "set1") or not c.has_option("ttest%i" % i, "set2"):
                print "[Nicessa] T-test %i is missing one or both data set descriptions." % i
                break

            tester.ttest(expfolder, c, i)
            i += 1


def list_data(expfolder):
    """ List the runs that have been made.

        :param string expfolder: relative path to expfolder
    """
    print "[Nicessa] The configurations and number of runs made so far:\n"
    for exp in utils.get_experiment_names(utils.get_main_conf(expfolder)):
        print "%s" % exp
        # get a list w/ relevant params
        cp = ConfigParser()
        expdirs = [d for d in os.listdir("%s/data" % expfolder) if d.startswith(exp)]
        if len(expdirs) == 0:
            print "No runs found for experiment %s\n" % exp
            continue
        onedir = "%s/data/%s" % (expfolder, expdirs[0])
        cp.read("%s/%s" % (onedir, [f for f in os.listdir(onedir) if f.endswith('.conf')][0]))
        params = cp.options('params')
        charlen = 1 + sum([len(p) + 6 for p in params]) + 9
        print '-' * charlen
        print "|",
        for p in params:
            print "  %s  |" % v ,
        print "| runs |"
        print '-' * charlen
        # now show how much we have in each relevant dir
        for dir in [d for d in os.listdir("%s/data" % expfolder) if d.startswith(exp)]:
            #print "%s | %d" % (d.ljust(70), utils.runs_in_folder(expfolder, d))
            cp = ConfigParser()
            path2dir = "%s/data/%s" % (expfolder, dir)
            cp.read("%s/%s" % (path2dir, [f for f in os.listdir(path2dir) if f.endswith('.conf')][0]))
            print "|",
            this_params = cp.options('params')
            for p in params:
                print "  %s|" % cp.get('params', p).ljust(len(p) + 2) ,
            print "| %s |" % str(utils.runs_in_folder(expfolder, dir)).rjust(4)
            print '-' * charlen


# ---------------------------------------------------------------------------------------------------

def _prepare(expfolder, limit_to={}, more=False):
    """ clean data, fill config directory with all subconfigs we want
        limit_to can contain parameter settings we want to limit ourselves to (this is in case we add more data)

        :param string expfolder: relative path to expfolder
        :param dict limit_to: key-value pairs that narrow down the dataset, when empty (default) all possible configs are run
        :param boolean more: when True, new data will simply be added to existing data
    """
    from sim import setup
    if osp.exists("%s/data" % expfolder) and not more:
        rmtree('%s/data' % expfolder)
    if not osp.exists("%s/data" % expfolder):
        os.mkdir('%s/data' % expfolder)
    if osp.exists("%s/conf" % expfolder):
        rmtree('%s/conf' % expfolder)

    conf = utils.get_main_conf(expfolder)
    setup.create(conf, expfolder, limit_to=limit_to, more=more)



if __name__ == "__main__":
    from sim import utils

    if len(sys.argv) < 2:
        utils.usage()

    expfolder = sys.argv[1].strip('/')
    conf = utils.get_main_conf(expfolder)

    opts, args = utils.read_args()
    do_run = do_results = do_plots = do_ttests = do_check = do_more = do_list = False

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            utils.usage()
        elif opt == "--run":
            do_run = True
        elif opt == "--check":
            do_check = True
            do_results = do_plots = False
            break
        elif opt ==  "--results":
            do_results = True
        elif opt ==  "--plots":
            do_plots = True
        elif opt == "--ttests":
            do_ttests = True
        elif opt == "--more":
            do_more = True
        elif opt == "--list":
            do_list = True

    # if nothing special is selected, do standard program
    if do_run == do_results == do_check == do_plots == do_ttests == do_more == do_list == False:
        do_run = do_plots = do_ttests = True
        if utils.is_remote(expfolder) or utils.cpus_per_host(expfolder)[1] > 1:
            do_results = True

    # only one of these at a time:
    if do_run:
        _prepare(expfolder)
        run_experiment(expfolder)
    elif do_check:
        from sim.net import remote
        remote.check(expfolder)
    elif do_more:
        run_more(expfolder)

    if do_results:
        from sim.net import remote
        from sim import setup
        # create confs (again) so we know what we expect to find on which host
        if not do_run:
            _prepare(expfolder)
        remote.get_results(expfolder, do_wait=do_run)

    if do_plots:
        make_plots(expfolder)

    if do_ttests:
        run_ttests(expfolder)

    if do_list:
        list_data(expfolder)

