'''
utils
=====
'''

#TODO: maybe there can be two utils, one for sim, one for analysis?


import sys
import os
import os.path as osp
import re
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError, NoSectionError, ParsingError
try:
	import argparse
except ImportError:
	print("[Nicessa] Import error: You need Python 2.7+ unless you have the argparse module installed independently.")
	sys.exit(1)



def read_args():
    """
    read in cmd line arguments for Nicessa, print usage if something is unexpected
    :returns: arg object returned by argparse
    """
    parser = argparse.ArgumentParser(description='Nicessa is an open-source toolkit for running parameterised stochastic simulations and analysing them.\
                                                  Please visit http://homepages.cwi.nl/~nicolas/nicessa')
    parser.add_argument('--folder', metavar='PATH', default='.', help='Path to simulation folder (this is where you keep your nicessa.conf), defaults to "."')
    parser.add_argument('--simulations', metavar='NAME', nargs='*', help='names of subsimulations (the filenames of their configuration files without the ".conf" ending).')
    parser.add_argument('--run', action='store_true', help='Only run, do not get (remote) results and do not analyse.')
    parser.add_argument('--check', action='store_true', help='Check state on remote computers.')
    parser.add_argument('--results', action='store_true', help='Get results from remote computers.')
    parser.add_argument('--list', action='store_true', help='List number of runs made so far, per configuration.')
    parser.add_argument('--more', action='store_true', help='Add more runs to current state of config and data.')
    parser.add_argument('--plots', metavar='FIGURE', nargs='*', type=int, help='Make plots (needs gnuplot and eps2pdf installed). Add indices of figures as arguments if you only want to generate specific ones.')
    parser.add_argument('--ttests', action='store_true', help='Run T-tests (needs Gnu R installed).')
    parser.add_argument('--showscreen', metavar="INDEX", nargs=2, type=int, help='Show current output of a remote screen, e.g. "--show-screen 1 3" shows cpu 3 on host 1')
    parser.add_argument('-k', action='store_true', help='keep tmp analysis files')
    parser.add_argument('-d', action='store_true', help='delete old data withoput asking')

    return parser.parse_args()


def check_conf(simfolder):
    """
    check if nicessa.conf contains all necessary sections and options
    :param string simfolder: relative path to simfolder
    """
    conf = ConfigParser()
    try:
        conf.read("%s/nicessa.conf" % simfolder)
    except ParsingError, e:
        print "[NICESSA] %s" % e
        sys.exit(2)

    if not osp.exists("%s/nicessa.conf" % simfolder):
        print "[Nicessa] Cannot find nicessa.conf in the folder '%s' - Exiting..." % simfolder
        sys.exit(2)

    if not conf.has_section('meta') or not conf.has_option('meta', 'name'):
        print "[NICESSA] You need to tell me a name for this simulation. \
            Please define an option called 'name' in a section called 'meta'."
        sys.exit(2)

    if not conf.has_section('control') or not conf.has_option('control', 'executable'):
        print "[NICESSA] You need to tell me what script to execute. \
            Please define an option called 'executable' in a section called 'control'."
        sys.exit(2)

    if not conf.has_section('params'):
        print "[NICESSA] Warning: You have not defined a 'params' - section."


def get_main_conf(simfolder):
    """ Return ConfigParser object read from main conf, with all relevant
        subsimulation configs set

        :param string simfolder: relative path to simfolder
        :returns: ConfigParser object
    """
    conf = ConfigParser()
    try:
        assert(osp.exists('%s/nicessa.conf' % simfolder))
    except AssertionError:
        print "[Nicessa] Cannot find nicessa.conf in the folder '%s' - Exiting ..." % simfolder
        sys.exit(2)
    conf.read("%s/nicessa.conf" % simfolder)

    if not conf.has_section('meta'):
        conf.add_section('meta')
    try:
        def_user = os.getlogin()
    except OSError, e:
        def_user = os.getenv('USER')
    for (sec, opt, default) in\
            [('meta', 'name', 'A simulation run by Nicessa'),\
             ('meta', 'maintainer', def_user),\
             ('control', 'local', '1'),\
             ('control', 'runs', '1')]:
        if not conf.has_option(sec, opt):
            conf.set(sec, opt, default)

    args = read_args()
    if args.simulations:
        conf.set('simulations', 'configs', ','.join(args.simulations))
    if conf.has_section('simulations'):
        for c in [cf.strip() for cf in conf.get('simulations', 'configs').split(',')]:
            if not osp.exists("%s/%s.conf" % (simfolder, c)):
                print "[Nicessa] Warning: The file %s.conf does not exist!" % c

    return conf


def get_host_conf(simfolder):
    """ get (optional) host conf

        :param string simfolder: relative path to simfolder
        :returns: ConfigParser object
    """
    if not osp.exists("%s/remote.conf" % simfolder):
        print "[Nicessa] WARNING: simulation is configured to not run locally, but the file remote.conf couldn't be found!"
        sys.exit(1)
    conf = ConfigParser()
    conf.read("%s/remote.conf" % simfolder)
    return conf


def make_screen_name(simfolder, host, cpu):
    ''' make a screen name, out of:
          * the name of main simulation, cleaned of all special chars
          * used conf files
          * host number
          * cpu number
        One special case (until we implement a session management):

        :param string simfolder: relative path to simfolder
        :param number hostr: host number
        :param numer cpu: cpu numer
        :returns: a screen name
    '''
    nicessa_conf = get_main_conf(simfolder)
    sim_name = nicessa_conf.get('meta', 'name')
    conf_name = 'main'
    subsims = []
    if nicessa_conf.has_option('simulations', 'configs'):
        subsims = nicessa_conf.get('simulations', 'configs').split(',')
    if len(subsims) > 0:
        conf_name = '_'.join(subsims)
    rx = re.compile('\W+')
    return 'screen_%s_%s_%s_%s' % (rx.sub('_', sim_name).strip(), conf_name, str(host), str(cpu))


def make_simdir_name(simfolder):
    '''
    Nake the name for a simulation dir from the name of conf files
    [This and make_screen_name need overhaul and a common approach when
    a session management is implenented]
    '''
    nicessa_conf = get_main_conf(simfolder)
    sim_name = 'main'
    subsims = []
    if nicessa_conf.has_option('simulations', 'configs'):
        subsims = nicessa_conf.get('simulations', 'configs').split(',')
    if len(subsims) > 0:
        sim_name = '_'.join(subsims)
    return sim_name



def get_subsimulation_names(conf):
    ''' get of simulation names.

        :param ConfigParser conf: main configuration
        :returns: a list with names, if no subsimulations are configured, the list will have an empty string as only element
    '''
    sim_names = ['']
    if 'simulations' in conf.sections() and conf.get('simulations', 'configs') != '':
        sim_names = conf.get('simulations', 'configs').split(',')
    return sim_names


def get_simulation_name(conf_filename, fallback):
    ''' The user can give a pretty name to the simulation under [meta], this function gets it.

        :param string conf_filename: name of the config file for the simulation
        :param string fallback: return this if the user didn't specify any
        :returns: string pretty name
    '''
    conf = ConfigParser()
    conf.read(conf_filename)
    if conf.has_option('meta', 'name'):
        return conf.get('meta', 'name')
    else:
        return fallback


def ensure_name(simfolder):
    ''' make sure we have the actual name of the folder and not just '.'

        :param string simfolder: relative path to simfolder
        :returns: the full name (without the path to it)
    '''
    if simfolder == '.':
        simfolder = osp.abspath(osp.curdir).split('/')[-1:][0]
    return simfolder.strip('/')


def is_remote(simfolder):
    '''
        :returns: True if the user configured the simulation to be run remotely
        :param string simfolder: relative path to simfolder
    '''
    conf = get_main_conf(simfolder)
    return conf.get("control", "local") != "1"


def num_hosts(simfolder):
    ''' :returns: how many hosts will be used
        :param string simfolder: relative path to simfolder
    '''
    if not is_remote(simfolder):
        return 1
    remote_conf = get_host_conf(simfolder)
    hosts = 0
    if remote_conf.has_section('host0'):
        print '[NICESSA] Please number your hosts starting with 1. Ignoring host0 ...'
    while remote_conf.has_section('host%d' % (hosts+1)):
        hosts += 1
    if hosts == 0:
        hosts = 1
    return hosts


def cpus_per_host(simfolder):
    ''' :returns: a dict, mapping host indices to the number of cpus specified for them to be available
        :param string simfolder: relative path to simfolder
    '''
    if not is_remote(simfolder):
        return {1:1}
    hosts = num_hosts(simfolder)
    cpus_per_host = dict.fromkeys(xrange(1, hosts+1), 0)
    if osp.exists("%s/remote.conf" % simfolder):
        remote_conf = ConfigParser()
        remote_conf.read("%s/remote.conf" % simfolder)
        for i in xrange(1, hosts+1):
            cpus_per_host[i] = remote_conf.getint("host%d" % i, "cpus")
    #else:
    #    cpus_per_host[0] = 1 # poor guy gets everything either way, so this need not be true
    return cpus_per_host


def working_cpus_per_host(simfolder):
    ''' :returns: a dict, mapping host indices to the number of cpus that have been assigned work on them
        :param string simfolder: relative path to simfolder
    '''
    if not os.path.exists('%s/conf' % simfolder):
        return cpus_per_host(simfolder)
    d = dict.fromkeys(xrange(1, num_hosts(simfolder)+1), 0)
    for host in d.keys():
        #TODO: this relies on the conf directory not having changed since the run was started ...
        #      there should be a better way, probably saving a session
        #      state somewhere ...
        if os.path.exists('%s/conf/%d' % (simfolder, host)):
            d[host] = len(os.listdir('%s/conf/%d' % (simfolder, host)))
    return d


def runs_in_folder(simfolder, fname):
    ''' :returns: number of runs that have been made in this data folder
        :param string simfolder: relative path to simfolder
    '''
    fpath = "%s/data/%s" % (simfolder, fname)
    if not os.path.exists(fpath):
        return 0
    logfiles = [f for f in os.listdir(fpath) if f.startswith('log') and f.endswith('.dat')]
    if len(logfiles) == 0:
        return 0
    log_numbers = [int(f.split('.')[0][3:]) for f in logfiles]
    return max(log_numbers)


def get_relevant_confs(simfolder):
    ''' :returns: ConfigParser objects for all config files being used
        :param string simfolder: relative path to simfolder
    '''
    conf = get_main_conf(simfolder)
    relevant_confs = [conf]
    if conf.has_section('simulations'):
        for subsim in conf.get('simulations', 'configs').split(','):
            c = ConfigParser()
            c.read("%s/%s.conf" % (simfolder, subsim))
            relevant_confs.append(c)
    return relevant_confs


def get_delimiter(conf):
    ''' get the delimiter used in the log files between values

        :param ConfigParser conf: the main config file
        :returns: the user-defined delimiter or the assumed default one (,)
    '''
    if conf.has_option('control', 'delimiter'):
        d = conf.get('control', 'delimiter')
        d = d.replace('\\t', '\t')
        return d
    else:
        return ','


def decode_search_from_confstr(s, sim=""):
    ''' Make dict out of configuration string that describes a search for a sub-dataset (for plots, ttests)

        :param string s: a string of comma-separated key-value pairs
        :returns: dictionary made from the string
    '''
    d = {}
    # prepare to deal with special chars
    s = s.replace('\\\\,', '\\ ,')
    s = s.replace('\\\\:', '\\ :')
    s = s.replace('\\,', "#COMMA#")
    s = s.replace('\\:', "#COLON#")
    s = s.replace('\\\\', '\\')

    for item in s.split(','):
        if item == '':
            continue
        try:
            k, v = item.split(':')
            v = v.replace("#COMMA#", ',')
            v = v.replace("#COLON#", ':')
        except:
            print '[NICESSA] Misconfiguration in Experiment %s while parsing "%s". This is the plot configuration, please check: "%s" ... ' % (sim, item, s)
            continue
        d[k.strip()] = v.strip()
    return d
