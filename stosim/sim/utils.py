'''
utils
=====
'''

#TODO: refactor this module:
# 1. make this a submodule, maybe residing in the main dir, then three files:
#    sim.py, remote.py and analysis.py (the latters would have at least decode_search_from_confstr)
# 2. There should be classes (as own files?) to represent the two major confs: stosim.conf and 
#    remote.conf. This would make code cleaner. Instantiate them with the
#    location of the conf and then put all access and check functions in them
#    Notes:
#    - They should make the original ConfigParser available as conf.cp 
#    - get_main_conf could maybe go to __init__
# 3. Some functions in stosim.py could go in one of those subfiles, thus making
#    that mode readable as well (not sure yet where the primary functionality
#    should go, maybe sim/__init__.py, analysis/__init__.py and so on, or
#    classes? 
# 4. While doing this, look out for PEP8 compatibility

import sys
import os
import os.path as osp
import re
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError, NoSectionError, ParsingError
try:
	import argparse
except ImportError:
	print("[StoSim] Import error: You need Python 2.7+ (you can, however, copy the argparse module inside your local directory.")
	sys.exit(1)



def read_args():
    """
    read in cmd line arguments for StoSim, print usage if something is unexpected
    :returns: arg object returned by argparse
    """
    parser = argparse.ArgumentParser(description='StoSim is an open-source toolkit for running parameterised stochastic simulations and analysing them.\
                                                  Please visit http://homepages.cwi.nl/~nicolas/stosim')
    parser.add_argument('--folder', metavar='PATH', default='.', help='Path to simulation folder (this is where you keep your stosim.conf), defaults to "."')
    parser.add_argument('--simulations', metavar='NAME', nargs='*', help='names of subsimulations (the filenames of their configuration files without the ".conf" ending).')
    parser.add_argument('--run', action='store_true', help='Only run, do not analyse.')
    parser.add_argument('--list', action='store_true', help='List number of runs made so far, per configuration.')
    parser.add_argument('--more', action='store_true', help='Add more runs to current state of config and data.')
    parser.add_argument('--plots', metavar='FIGURE', nargs='*', type=int, help='Make plots (needs gnuplot and eps2pdf installed). Add indices of figures as arguments if you only want to generate specific ones.')
    parser.add_argument('--ttests', action='store_true', help='Run T-tests (needs Gnu R installed).')
    parser.add_argument('-k', action='store_true', help='keep tmp analysis files.')
    parser.add_argument('-d', action='store_true', help='delete old data without confirmation.')

    return parser.parse_args()


def check_conf(simfolder):
    """
    check if stosim.conf contains all necessary sections and options
    :param string simfolder: relative path to simfolder
    """
    conf = ConfigParser()
    try:
        conf.read("%s/stosim.conf" % simfolder)
    except ParsingError, e:
        print "[StoSim] %s" % e
        sys.exit(2)

    if not osp.exists("%s/stosim.conf" % simfolder):
        print "[StoSim] I can not find stosim.conf in the folder '%s' - Exiting..." % simfolder
        sys.exit(2)

    if not conf.has_section('meta') or not conf.has_option('meta', 'name'):
        print "[StoSim] You need to tell me a name for this simulation. \
            Please define an option called 'name' in a section called 'meta'."
        sys.exit(2)

    if not conf.has_section('control') or not conf.has_option('control', 'executable'):
        print "[StoSim] You need to tell me what script to execute. \
            Please define an option called 'executable' in a section called 'control'."
        sys.exit(2)

    if not conf.has_section('params'):
        print "[StoSim] Warning: You have not defined a 'params' - section."


def get_main_conf(simfolder):
    """ Return ConfigParser object read from main conf, with all relevant
        subsimulation configs set

        :param string simfolder: relative path to simfolder
        :returns: ConfigParser object
    """
    conf = ConfigParser()
    try:
        assert(osp.exists('%s/stosim.conf' % simfolder))
    except AssertionError:
        print "[StoSim] Cannot find stosim.conf in the folder '%s' - Exiting ..." % simfolder
        sys.exit(2)
    conf.read("%s/stosim.conf" % simfolder)

    if not conf.has_section('meta'):
        conf.add_section('meta')
    try:
        def_user = os.getlogin()
    except OSError, e:
        def_user = os.getenv('USER')
    for (sec, opt, default) in\
            [('meta', 'name', 'A simulation run by StoSim'),\
             ('meta', 'maintainer', def_user),\
             ('control', 'scheduler', 'fjd'),\
             ('control', 'runs', '1')]:
        if not conf.has_option(sec, opt):
            conf.set(sec, opt, default)

    args = read_args()
    if args.simulations:
        if not conf.has_section('simulations'):
            print "[StoSim] You cannot use the '--simulations' cmd line"\
                  " parameter if you do not have the [simulations] section"\
                  " in stosim.conf"
            sys.exit(2)
        conf.set('simulations', 'configs', ','.join(args.simulations))
    if conf.has_section('simulations'):
        for c in [cf.strip() for cf in conf.get('simulations', 'configs').split(',')]:
            if not osp.exists("%s/%s.conf" % (simfolder, c)):
                print "[StoSim] Warning: The file %s.conf does not exist!" % c

    return conf

def get_combined_conf(simfolder):
    ''' 
        Make a configuration with all used params and their values - this 
        means we gathe all param values from eventual subconfs,
        next to stosim.conf
        
        :param string simfolder: relative path to simfolder
        :returns: ConfigParser combined conf

    '''
    conf = get_main_conf(simfolder)
    if conf.has_section('simulations'):
        configs = conf.get('simulations', 'configs').split(',')
        for c in [cf.strip() for cf in configs]:
            subconf = ConfigParser()
            subconf.read('{}/{}.conf'.format(simfolder, c))
            for p in subconf.options('params'):
                if conf.has_option('params', p):
                    both = conf.get('params', p).split(',')
                    both.extend(subconf.get('params', p).split(','))
                    conf.set('params', p, ','.join(set(both)))
                else:
                    conf.set('params', p, subconf.get('params', p))
    return conf


def get_scheduler(simfolder):
    """ get the scheduler (fjd or pbs)

        :param string simfolder: relative path to simfolder
        :returns: string scheduler
    """
    stosim_conf = get_main_conf(simfolder)
    if not stosim_conf.has_option('control', 'scheduler'):
        scheduler = "fjd"
    else:
        scheduler = stosim_conf.get('control', 'scheduler')
    if not scheduler in ('fjd', 'pbs'):
        print("[StoSim] {} is not a valid scheduler.".format(scheduler))
        scheduler = "fjd"
    return scheduler


def get_interval(simfolder):
    """ get the interval for FJD  workers and disoatchers to check the queue,
        in seconds (fractions of seconds are allowed).

        :param string simfolder: relative path to simfolder
        :returns: float interval
    """
    stosim_conf = get_main_conf(simfolder)
    if not stosim_conf.has_option('control', 'fjd-interval'):
        interval = .2
    else:
        interval = stosim_conf.getfloat('control', 'fjd-interval')
    return interval


def get_jobtime(simfolder):
    """ get the expected maximal jobtime for PBS jobs,
        the format is HH:MM:SS

        :param string simfolder: relative path to simfolder
        :returns: string jobtime
    """
    stosim_conf = get_main_conf(simfolder)
    if not stosim_conf.has_option('control', 'pbs-jobtime'):
        jobtime = '00:05:00'
    else:
        jobtime = stosim_conf.get('control', 'pbs-jobtime')
    return jobtime


def make_simdir_name(simfolder):
    '''
    Make the name for a simulation dir from the simulation name and the name of conf files
    [This and make_screen_name need overhaul and a common approach when
    a session management is implemented]

    :param string simfolder: relative path to simfolder
    '''
    stosim_conf = get_main_conf(simfolder)
    sim_name = stosim_conf.get('meta', 'name')
    simdir_name = 'main'
    subsims = get_subsimulation_names(stosim_conf)
    if subsims != ['']:
        simdir_name = '_'.join(subsims)
    rx = re.compile('\W+')
    return '%s_%s' % (rx.sub('_', sim_name).strip(), simdir_name)


def get_subsimulation_names(conf):
    ''' get sub-simulation config names.

        :param ConfigParser conf: main configuration
        :returns: A list with names. If no subsimulations are configured, the list will have an empty string as only element
    '''
    sim_names = ['']
    if 'simulations' in conf.sections() \
            and conf.has_option('simulations', 'configs')\
            and conf.get('simulations', 'configs') != '':
        sim_names = conf.get('simulations', 'configs').split(',')
    sim_names = [s.strip() for s in sim_names]
    return sim_names


def get_simulation_name(conf_filename, fallback):
    ''' The user can give a pretty name to the simulation under [meta], this function returns it.

        :param string conf_filename: name of the config file for the simulation
        :param string fallback: return this if the user didn't specify any
        :returns: string pretty name
    '''
    conf = ConfigParser()
    conf.read(conf_filename)
    if conf.has_option('meta', 'name'):
        return conf.get('meta', 'name').replace(' ', '_')
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
            filename = subsim.strip()
            c.read("%s/%s.conf" % (simfolder, filename))
            c.set('meta', '_subconf-filename_', filename)
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
            print '[StoSim] Misconfiguration in Experiment %s while parsing "%s". This is the plot configuration, please check: "%s" ... ' % (sim, item, s)
            continue
        d[k.strip()] = v.strip()
    return d
