'''
utils
=====
'''

#TODO: maybe there can be two utils, one for sim, one for analysis?


import sys
import os
import os.path as osp
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError, NoSectionError
import getopt


def read_args():
    """ read in cmd line arguments for Nicessa, print usage if something is unexpected """
    try:
        return getopt.getopt(sys.argv[2:], "hk", ["help", "simulations=", "run", "check", "results", "plots", "ttests", "more", "list"])
    except getopt.GetoptError, e:
        print '[Nicessa] %s\n' % e
        usage()


def usage():
    """ print usage and exit """
    print "[Nicessa] usage: nicessa.py <path-to-simulation-folder> [--simulations=X,Y]"\
          " [--run] [--check] [--results] [--plots] [--ttests] [--more] [--list]"
    print "(the simulation folder is where you have your simulation.conf)"
    print "(If you run things on remote hosts you will need paramiko)\n"
    w = 25
    print "%s : names of subsimulations (without '.conf', e.g. 'sim1,sim2')" % '--simulations'.ljust(w)
    print "%s : Only run, do not get (remote) results and do not analyse" % '--run'.ljust(w)
    print "%s : Check state of remote computers" % '--check'.ljust(w)
    print "%s : Get results from remote computers" % '--results'.ljust(w)
    print "%s : List number of runs made so far, per configuration" % '--list'.ljust(w)
    print "%s : Add more runs to current state of config and data" % '--more'.ljust(w)
    print "%s : Make plots (needs gnuplot and eps2pdf installed))" % '--plots'.ljust(w)
    print "%s : Run T-tests (needs R installed)" % '--ttests'.ljust(w)
    sys.exit(2)


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
        print "[Nicessa] Warning: The file %s/nicessa.conf does not exist!" % simfolder
        sys.exit(2)

    needed = [('meta', 'name'),
              ('meta', 'maintainer'),
              ('control', 'executable'),
              ('control', 'local'),
              ('control', 'runs')
             ]
    for n in needed:
        try:
            _ = conf.get(n[0], n[1])
        except NoSectionError, e:
            print "[NICESSA] %s" % e
            sys.exit(2)
        except NoOptionError, e:
            print "[NICESSA] %s" % e
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
        print "[Nicessa] WARNING: Cannot find nicessa.conf in the folder %s." % simfolder
        sys.exit()
    conf.read("%s/nicessa.conf" % simfolder)
    # overwrite simulation-configs
    # first see if there are some passed as params (then we use those)
    opts, args = read_args()
    for opt, arg in opts:
        if opt in ("--simulations="):
            s = []
            for a in arg.split(','):
                s.append(a)
            conf.set('simulations', 'configs', ','.join(s))
    # then set all the params from subconfs
    if conf.has_section('simulations'):
        for c in conf.get('simulations', 'configs').split(','):
            if not osp.exists("%s.conf" % c):
                print "[Nicessa] Warning: The file %s.conf does not exist!" % c
            else:
                subconf = ConfigParser()
                subconf.read('%s/%s.conf' % (simfolder, c))
                for p in subconf.options('params'):
                    if conf.has_option('params', p):
                        both = conf.get('params', p).split(',')
                        both.extend(subconf.get('params', p).split(','))
                        conf.set('params', p, ','.join(set(both)))
                    else:
                        conf.set('params', p, subconf.get('params', p))
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


def get_simulation_names(conf):
    ''' get of simulation names.

        :param ConfigParser conf: main configuration
        :returns: a list with names, if no subsimulations are configured, the list will have an empty string as only element
    '''
    sim_names = ['']
    if 'simulations' in conf.sections() and conf.get('simulations', 'configs') != '':
        sim_names = conf.get('simulations', 'configs').split(',')
    return sim_names


def get_pretty_simulation_name(conf_filename, fallback):
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
    # 4 rows per host in host conf
    hosts = 0
    while remote_conf.has_section('host%d' % (hosts+1)):
        hosts += 1
    if hosts == 0:
        hosts = 1
    return hosts


def cpus_per_host(simfolder):
    ''' :returns: a dict, mapping host indices to the number of cpus specified for them
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


def runs_in_folder(simfolder, fname):
    ''' :returns: number of runs that have been made in this data folder
        :param string simfolder: relative path to simfolder
    '''
    fpath = "%s/data/%s" % (simfolder, fname)
    if not os.path.exists(fpath):
        return 0
    logfiles = [f for f in os.listdir(fpath) if f.startswith('log') and f.endswith('.csv')]
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
        try:
            k, v = item.split(':')
            v = v.replace("#COMMA#", ',')
            v = v.replace("#COLON#", ':')
        except:
            print '[NICESSA] Misconfiguration in Experiment %s while parsing "%s". This is the plot configuration, please check: "%s" ... ' % (sim, item, s)
            continue
        d[k.strip()] = v.strip()
    return d
