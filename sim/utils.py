'''
utils
=====
'''

#TODO: maybe there can be two utils, one for sim, one for analysis?


import sys
import os
import os.path as osp
from ConfigParser import ConfigParser
import getopt


def read_args():
    """ read in cmd line arguments for Nicessa, print usage if something is unexpected """
    try:
        return getopt.getopt(sys.argv[2:], "hk", ["help", "experiments=", "run", "check", "results", "plots", "ttests", "more", "list"])
    except getopt.GetoptError, e:
        print '[Nicessa] %s\n' % e
        usage()


def usage():
    """ print usage and exit """
    print "[Nicessa] usage: experiment.py <path-to-experiment-folder> [--experiments=X,Y]"\
          " [--run] [--check] [--results] [--plots] [--ttests] [--more] [--list]"
    print "(the experiment folder is where you have your experiment.conf)"
    print "(If you run things on remote hosts you will need paramiko)\n"
    w = 25
    print "%s : names of subexperiments (without '.conf', e.g. 'exp1,exp2')" % '--experiments'.ljust(w)
    print "%s : Only run, do not get (remote) results and do not analyse" % '--run'.ljust(w)
    print "%s : Check state of remote computers" % '--check'.ljust(w)
    print "%s : Get results from remote computers" % '--results'.ljust(w)
    print "%s : List number of runs made so far, per configuration" % '--list'.ljust(w)
    print "%s : Add more runs to current state of config and data" % '--more'.ljust(w)
    print "%s : Make plots (needs gnuplot and eps2pdf installed))" % '--plots'.ljust(w)
    print "%s : Run T-tests (needs R installed)" % '--ttests'.ljust(w)
    sys.exit(2)


def get_main_conf(expfolder):
    """ Return ConfigParser object read from main conf, with all relevant
        subexperiment configs set

        :param string expfolder: relative path to expfolder
        :returns: ConfigParser object
    """
    conf = ConfigParser()
    try:
        assert(osp.exists('%s/experiment.conf' % expfolder))
    except AssertionError:
        print "[Nicessa] WARNING: Cannot find experiment.conf in the folder %s." % expfolder
        sys.exit()
    conf.read("%s/experiment.conf" % expfolder)
    opts, args = read_args()
    for opt, arg in opts:
        if opt in ("--experiments="):
            s = []
            for a in arg.split(','):
                if a in conf.get('experiments', 'configs').split(','):
                    s.append(a)
                if not osp.exists("%s.conf" % a):
                    print "[Nicessa] Warning: The file %s.conf does not exist!" % a
            conf.set('experiments', 'configs', ','.join(s))
    return conf


def get_host_conf(expfolder):
    """ get (optional) host conf

        :param string expfolder: relative path to expfolder
        :returns: ConfigParser object
    """
    if not osp.exists("%s/remote.conf" % expfolder):
        print "[Nicessa] WARNING: experiment is configured to not run locally, but the file remote.conf couldn't be found!"
        sys.exit(1)
    conf = ConfigParser()
    conf.read("%s/remote.conf" % expfolder)
    return conf


def get_experiment_names(conf):
    ''' get of experiment names.

        :param ConfigParser conf: main configuration
        :returns: a list with names, if no subexperiments are configured, the list will have an empty string as only element
    '''
    expnames = ['']
    if 'experiments' in conf.sections() and conf.get('experiments', 'configs') != '':
        expnames = conf.get('experiments', 'configs').split(',')
    return expnames


def get_pretty_experiment_name(conf_filename, fallback):
    ''' The user can give a pretty name to the experiment under [meta], this function gets it.

        :param string conf_filename: name of the config file for the experiment
        :param string fallback: return this if the user didn't specify any
        :returns: string pretty name
    '''
    conf = ConfigParser()
    conf.read(conf_filename)
    if conf.has_option('meta', 'name'):
        return conf.get('meta', 'name')
    else:
        return fallback


def ensure_name(expfolder):
    ''' make sure we have the actual name of the folder and not just '.'

        :param string expfolder: relative path to expfolder
        :returns: the full name (without the path to it)
    '''
    if expfolder == '.':
        expfolder = osp.abspath(osp.curdir).split('/')[-1:][0]
    return expfolder.strip('/')


def is_remote(expfolder):
    '''
        :returns: True if the user configured the experiment to be run remotely
        :param string expfolder: relative path to expfolder
    '''
    conf = get_main_conf(expfolder)
    return conf.get("control", "local") != "1"


def num_hosts(expfolder):
    ''' :returns: how many hosts will be used
        :param string expfolder: relative path to expfolder
    '''
    if not is_remote(expfolder):
        return 1
    remote_conf = get_host_conf(expfolder)
    # 4 rows per host in host conf
    hosts = 0
    while remote_conf.has_section('host%d' % (hosts+1)):
        hosts += 1
    if hosts == 0:
        hosts = 1
    return hosts


def cpus_per_host(expfolder):
    ''' :returns: a dict, mapping host indices to the number of cpus specified for them
        :param string expfolder: relative path to expfolder
    '''
    if not is_remote(expfolder):
        return {1:1}
    hosts = num_hosts(expfolder)
    cpus_per_host = dict.fromkeys(xrange(1, hosts+1), 0)
    if osp.exists("%s/remote.conf" % expfolder):
        remote_conf = ConfigParser()
        remote_conf.read("%s/remote.conf" % expfolder)
        for i in xrange(1, hosts+1):
            cpus_per_host[i] = remote_conf.getint("host%d" % i, "cpus")
    #else:
    #    cpus_per_host[0] = 1 # poor guy gets everything either way, so this need not be true
    return cpus_per_host


def runs_in_folder(expfolder, fname):
    ''' :returns: number of runs that have been made in this data folder
        :param string expfolder: relative path to expfolder
    '''
    fpath = "%s/data/%s" % (expfolder, fname)
    if not os.path.exists(fpath):
        return 0
    logfiles = [f for f in os.listdir(fpath) if f.startswith('log') and f.endswith('.csv')]
    if len(logfiles) == 0:
        return 0
    log_numbers = [int(f.split('.')[0][3:]) for f in logfiles]
    return max(log_numbers)


def get_relevant_confs(expfolder):
    ''' :returns: ConfigParser objects for all config files being used
        :param string expfolder: relative path to expfolder
    '''
    conf = get_main_conf(expfolder)
    relevant_confs = [conf]
    if conf.has_section('experiments'):
        for subexp in conf.get('experiments', 'configs').split(','):
            c = ConfigParser()
            c.read("%s/%s.conf" % (expfolder, subexp))
            relevant_confs.append(c)
    return relevant_confs


def decode_search_from_confstr(s, exp=""):
    ''' Make dict out of configuration string that describes a search for a sub-dataset (for plots, ttests)

        :param string s: a string of comma-separated key-value pairs
        :returns: dictionary made from the string
    '''
    d = {}
    for item in s.split(','):
        try:
            [k, v] = item.split(':')
        except:
            print '[NICESSA] Misconfiguration in Experiment %s. Please check: [%s] ... ' % (exp, s)
            continue
        d[k.strip()] = v.strip()
    return d
