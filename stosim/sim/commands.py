'''
commands
=============

This module provides all commands you can use in StoSim:
run, resume, status, kill, snapshot, run_more, make_plots, run_ttests, list_data
'''


import sys
import os
import os.path as osp
import subprocess
try:
    import configparser
except ImportError:
    import ConfigParser as configparser  # for py2
from shutil import rmtree


from shutil import copy

import fjd

from stosim.sim import utils
from stosim.analysis import plotter, tester
from stosim.sim.job_creator import create_jobs


if sys.version < '3':
    input = raw_input


we_exited = [False]  # this helps us to stop using FJD if the user quit

def run(simfolder):
    ''' The main function to start running simulations

        :param string simfolder: relative path to simfolder
        :returns: True if successful, False otherwise
    '''
    print('*' * 80)
    sim_name = utils.get_simulation_name(simfolder, "{}/stosim.conf".format(simfolder))
    print("Running simulation {}".format(sim_name))
    print('*' * 80)
    print('')

    if not osp.exists("%s/stosim.conf" % simfolder):
        print("[StoSim] %s/stosim.conf does not exist!" % simfolder)
        utils.usage()
        return False

    # prepare all jobs to be run by FJD
    fjd_dir = fjd.utils.ensure_wdir(sim_name)
    fjd.utils.empty_queues(sim_name)
    for job in [j for j in os.listdir("{}/jobs".format(simfolder))\
                if j.endswith('.conf')]:
        copy("{}/jobs/{}".format(simfolder, job),
             "{}/jobqueue".format(fjd_dir))
    dispatch_cmd = 'fjd-dispatcher --project {} --end_when_jobs_are_done '\
                   ' --callback "stosim --kill" --interval {}'\
                   .format(sim_name, utils.get_interval(simfolder))

    # now decide if recruiting is done in a local network or on a PBS cluster
    scheduler = utils.get_scheduler(simfolder)
    if scheduler == 'fjd':
        # let FJD handle it in local network (default: only local PC)
        if os.path.exists('{}/remote.conf'.format(simfolder)):
            copy('{}/remote.conf'.format(simfolder), fjd_dir)
        subprocess.call('fjd-recruiter --project {} hire'.format(sim_name), shell=True)
        if not we_exited[0]:
            subprocess.call(dispatch_cmd, shell=True)
        # when recruiter got remote.conf, clean up in fjd dir
        if os.path.exists('{}/remote.conf'.format(simfolder)):
            os.remove('{}/remote.conf'.format(fjd_dir))

    elif scheduler == 'pbs':
        # queue the PBS jobs we created on a PBS job scheduler (e.g. clusters 
        # running Torque or PBS Pro). These simply start FJD workers.
        for job in [j for j in os.listdir('{}/jobs'.format(simfolder)) if j.endswith('.pbs')]:
            subprocess.call('qsub {}'.format('{}/jobs/{}'.format(simfolder, job)), shell=True)
        # Now we start dispatching
        subprocess.call(dispatch_cmd, shell=True)

    return True


def resume(simfolder):
    """
    (Re)start dispatching jobs 

    :param string simfolder: relative path to simfolder
    :returns: True if successful, False otherwise
    """
    sim_name = utils.get_simulation_name(simfolder, "{}/stosim.conf".format(simfolder))
    subprocess.call('fjd-dispatcher --project {} --interval {}'\
          .format(sim_name, utils.get_interval(simfolder)), shell=True)
    return True


def status(simfolder):
    """
    Check status of simulation. If on PBS scheduling, show status of nodes.
    Then, ask the fjd-dispatcher about status of jobs.

    :param string simfolder: relative path to simfolder
    :returns: True if successful, False otherwise
    """
    scheduler = utils.get_scheduler(simfolder)
    sim_name = utils.get_simulation_name(simfolder, "{}/stosim.conf".format(simfolder))
    if scheduler == 'pbs':
        num_nodes = len([n for n in os.listdir('{}/jobs'.format(simfolder))\
                        if n.endswith('.pbs')])
        if num_nodes > 0:
            print("[StoSim] State of our {} PBS computing nodes:".format(num_nodes))
            subprocess.call('echo "Waiting: $(qselect -u $USER -s W | wc -l)"', shell=True)
            subprocess.call('echo "Queued: $(qselect -u $USER -s Q | wc -l)"', shell=True)
            subprocess.call('echo "Running: $(qselect -u $USER -s R | wc -l)"', shell=True)
        else:
            print("[StoSim] No PBS computing nodes seem to be configured...")

    print("[StoSim] State of workers and jobs:")
    subprocess.call('fjd-dispatcher --project {} --status_only --interval {}'\
        .format(sim_name, utils.get_interval(simfolder)), shell=True)
    return True


def snapshot(simfolder, identifier=None):
    """
    Make a snapshot of the current state, using rsync with an example from
    http://schlutech.com/2011/11/rsync-full-incremental-differential-snapshots/

    :param string simfolder: relative path to simfolder
    :param string identifier: custom identifier for this snapshot
    :returns: True if successful, False otherwise
    """
    snapfolder = 'stosim-snapshots'
    date_format = "+%Y.%m.%d_%H:%M:%S"
    
    if not identifier:
        print('[StoSim] If wanted, enter a custom identifier:')
        identifier = input().replace(' ', '_')  # TODO: replace other characters?

    if not os.path.exists("{}/{}".format(simfolder, snapfolder)):
        os.mkdir("{}/{}".format(simfolder, snapfolder))
        rsync = 'rsync'
    else:
        rsync = 'link_dest=`find {abs_sf}/{ss} -maxdepth 1 -type d | sort | tail -n 1`;'\
                ' rsync --link-dest=${{link_dest}}'\
                .format(abs_sf=os.path.abspath(simfolder), ss=snapfolder)
   
    subprocess.call('cd {sf}; {rsync} -a --exclude {ss} --exclude \.svn --exclude \.git --exclude \.hg'\
                    ' . {ss}/`date {df}`_{ident}; cd {curdir}'\
                    .format(rsync=rsync, sf=simfolder, ss=snapfolder,
                            df=date_format, ident=identifier,
                            curdir=os.path.abspath(os.curdir)), shell=True)

    print('[StoSim] Made a new snapshot in {}/{}.'.format(simfolder, snapfolder))
    return True


def kill(simfolder):
    """
    Kill simulation
    Warning: On pbs, kills all your jobs (ignores --project)!
    """
    scheduler = utils.get_scheduler(simfolder)
    sim_name = utils.get_simulation_name(simfolder, "{}/stosim.conf".format(simfolder))
    if scheduler == 'fjd':
        subprocess.call('fjd-recruiter --project {} fire'.format(sim_name),
              shell=True)
    elif scheduler == 'pbs':
        subprocess.call('qselect -u $USER | xargs qdel', shell=True)

    return True



def run_more(simfolder):
    """ let the user make more runs on current config,
        in addition to the given data

        :param string simfolder: relative path to simfolder
        :returns: True if successful, False otherwise
    """
    simfolder = simfolder.strip('/')
    conf = utils.get_combined_conf(simfolder)

    print('''
[StoSim] Let's make {} more run(s)! Please tell me on which configurations.\n
Enter any parameter values you want to narrow down to, nothing otherwise."
'''.format(conf.getint('control', 'runs')))
    sel_params = {}
    for o in conf.options('params'):
        selected = False
        params = [p.strip() for p in conf.get('params', o).split(',')]
        if len(params) == 1:
            print("<{}> has only one value:".format(o))
            print(params[0])
            continue
        while not selected:
            choice = []
            print("<{}> ? (out of [{}])".format(o, conf.get('params', o)))
            for selection in input().split(','):
                selected = True
                if selection == "":
                    pass
                elif selection in params:
                    choice.append(selection)
                else:
                    print("Sorry, {} is not a valid value.".format(selection))
                    selected = False
        if len(choice) > 0:
            sel_params[o] = choice
        else:
            print("No restriction chosen.")
    print("You selected: {}. Do this? [Y|n]\n"\
          "(Remember that configuration and code should still be the same!)"\
                .format(str(sel_params)))
    if input().lower() in ["", "y"]:
        prepare_folders_and_jobs(simfolder, limit_to=sel_params, more=True)
        return run(simfolder)
    return False


def make_plots(simfolder, plot_nrs=[]):
    """ generate plots as specified in the simulation conf

        :param string simfolder: relative path to simfolder
        :param list plot_nrs: a list with plot indices. If empty, plot all
    """

    simfolder = simfolder.strip('/')

    #if osp.exists("%s/plots" % simfolder):
    #   rmtree('%s/plots' % simfolder)
    if not osp.exists("%s/plots" % simfolder):
        os.mkdir('%s/plots' % simfolder)

    # tell about what we'll do if we have at least one plot
    relevant_confs = utils.get_relevant_confs(simfolder)
    for c in relevant_confs:
        if c.has_section("figure1"):
            print('')
            print('*' * 80)
            print("[StoSim] creating plots ...")
            print('*' * 80)
            print('')
            break
    else:
        print("[StoSim] No plots specified.")

    # Describe all options first.
    # These might be set in plot-settings (in each simulation config)
    # and also per-figure
    general_options = {'use-colors': bool, 'use-tex': bool, 'line-width': int,
                       'font-size': int, 'infobox-pos': str,
                       'use-y-errorbars': bool, 'errorbar-every': int
                      }
    figure_specific_options = {
                       'name': str, 'xcol': int, 'x-range': str,
                       'y-range': str, 'x-label': str, 'y-label': str,
                       'custom-script': str
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
    c = configparser.ConfigParser()
    c.read('{}/stosim.conf'.format((simfolder)))
    delim = utils.get_delimiter(c)
    for o, t in general_options.items():
        get_opt_val(c, general_settings, 'plot-settings', o, t)
    general_params = []
    if c.has_option('plot-settings', 'params'):
        general_params = c.get('plot-settings', 'params').split(',')

    for c in relevant_confs:
        i = 1
        settings = general_settings.copy()
        # overwrite with plot-settings for this subsimulation
        for o, t in general_options.items():
            get_opt_val(c, settings, 'plot-settings', o, t)
        if c.has_option('plot-settings', 'params'):
            general_params.extend(c.get('plot-settings', 'params').split(','))

        while c.has_section("figure%i" % i):
            if i in plot_nrs or len(plot_nrs) == 0:
                fig_settings = settings.copy()
                for o, t in figure_specific_options.items():
                    get_opt_val(c, fig_settings, 'figure%i' % i, o, t)

                plot_confs = []
                j = 1
                while c.has_option("figure%i" % i, "plot%i" % j):
                    # make plot settings from conf string
                    d = utils.decode_search_from_confstr(
                            c.get('figure%i' % i, 'plot%i' % j),
                            sim=c.get('meta', 'name')
                        )
                    # then add general param settings to each plot, if
                    # not explicitly in there
                    for param in general_params:
                        if ":" in param:
                            param = param.split(':')
                            key = param[0].strip()
                            if not key in list(d.keys()):
                                d[key] = param[1].strip()
                    # add simulation file name, then we can select accordingly
                    if c.has_option('meta', '_subconf-filename_'):
                        scfn = c.get('meta', '_subconf-filename_')
                        if scfn != '' and not 'sim' in d:
                            d['sim'] = scfn
                    # making sure all necessary plot attributes are there
                    if ('_name' in list(d.keys())and '_ycol' in list(d.keys()) and
                        '_type' in list(d.keys())):
                        plot_confs.append(d)
                    else:
                        print('''
[StoSim] Warning: Incomplete graph specification in Experiment %s
- for plot {} in figure {}. \n
Specify at least _name and _ycol.'''.format((c.get('meta', 'name'), j, i)))
                    j += 1
                plotter.plot(filepath='%s/data' % simfolder,
                             delim=delim,
                             outfile_name='%s/plots/%s.pdf' \
                                % (simfolder, fig_settings['name']),\
                             plots=plot_confs,\
                             **fig_settings)
            i += 1


def run_ttests(simfolder):
    '''
    Make statistical t tests

    :param string simfolder: relative path to simfolder
    '''
    c = configparser.ConfigParser()
    c.read('{}/stosim.conf'.format((simfolder)))
    delim = utils.get_delimiter(c)

    relevant_confs = utils.get_relevant_confs(simfolder)

    # tell about what we'll do if we have at least one test
    for c in relevant_confs:
        if c.has_section("ttest1"):
            print('')
            print('*' * 80)
            print("[StoSim] Running T-tests ...")
            print('*' * 80)
            print('')
            break
    else:
        print("[StoSim] No T-tests specified.")

    for c in relevant_confs:
        i = 1

        while c.has_section("ttest%i" % i):
            print("Test {}:".format(c.get('ttest%i' % i, 'name').strip('"')))
            if not (c.has_option("ttest%i" % i, "set1") and
                    c.has_option("ttest%i" % i, "set2")):
                print("[StoSim] T-test {} is missing one or both"\
                      " data set descriptions.".format(i))
                break

            tester.ttest(simfolder, c, i, delim)
            i += 1


def list_data(simfolder):
    """ List the number of runs that have been made per configuration.

        :param string simfolder: relative path to simfolder
        :returns: True if successful, False otherwise
    """
    print("[StoSim] The configurations and number of runs made so far:\n")
    for sim in utils.get_subsimulation_names(utils.get_main_conf(simfolder)):
        print("Simulation: {}".format(sim))
        # get a list w/ relevant params from first-found config file
        # they should be the same
        data_dirs = os.listdir("%s/data" % simfolder)
        sim_dirs = [d for d in data_dirs if d.startswith("sim{}".format(sim))]
        if len(sim_dirs) == 0:
            print("No runs found for simulation {}\n".format(sim))
            continue
        conf = utils.get_combined_conf(simfolder)
        params = conf.options('params')
        charlen = 1 + sum([len(p) + 6 for p in params]) + 9
        print('-' * charlen)
        print("|"),
        for p in params:
            print("  {}  |".format(p)),
        print("| runs |")
        print('-' * charlen)
        # now show how much we have in each relevant dir
        for d in sim_dirs:
            print("|"),
            for p in params:
                v = d.split("_{}".format(p))[1].split("_")[0]
                print("  {}|".format(v.ljust(len(p) + 2))),
            print("| {} |".format(str(utils.runs_in_folder(simfolder, d)).rjust(4)))
            print('-' * charlen)
    return True


def prepare_folders_and_jobs(simfolder, limit_to={}, more=False):
    """ ensure that data and job directories exist, create jobs.
        limit_to can contain parameter settings we want
        to limit ourselves to (this is in case we add more data)

        :param string simfolder: relative path to simfolder
        :param dict limit_to: key-value pairs that narrow down the dataset,
                              when empty (default) all possible configs are run
        :param boolean more: when True, new data will simply be added
    """
    if not osp.exists("%s/data" % simfolder):
        os.mkdir('%s/data' % simfolder)
    if osp.exists("%s/jobs" % simfolder):
        rmtree('%s/jobs' % simfolder)
    os.mkdir('%s/jobs' % simfolder)

    conf = utils.get_main_conf(simfolder)
    create_jobs(conf, simfolder, limit_to=limit_to, more=more)
