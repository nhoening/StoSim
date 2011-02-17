#!/usr/bin/python

'''
setup
=====

This module sets up the stage - with it, you can make a configuration file
for each mix of parameter settings that needs to be run.

It also distributes them among the available hosts and cpus:
Each of them gets a directory, in which a main.conf file lists the other configs.
'''

import sys
import os
from ConfigParser import ConfigParser
from shutil import rmtree

import utils



def create(conf, expfolder, limit_to={}, more=False):
    """
    Writes a conf file for each run that the parameters in conf suggest.
    Also divides all runs of an experiment in groups with a main conf each, to run on different hosts.

    :param ConfigParser conf: main configuration
    :param string expfolder: relative path to expfolder
    :param dict limit_to: dict of configuration settings we should limit to (default is an empty dict)
    :param boolean more: True if runs should be appended to existing data (default is False)
    """

    # ---------------------------------------------------------------------------------------------
    # define some helpful functions

    def combiner(lists):
        '''
        :param list lists: list of lists with inputs
        :returns: all possible combinations of the input items in a nested list
        '''
        res = [[]]
        for l in lists:
            tmp = []
            for i in l:
                for j in res:
                    tmp.append(j+[i])
            res = tmp
        return res


    def get_options_values(exp_params, limit_to):
        '''
        :param dict exp_params: dict of configuration for one experiment
        :param dict limit_to: dict of configuration settings we should limit to
        :returns: a list of option names and lists of values to use in every possible combination in one experiment.
        '''
        comb_options = [] # all my param names
        comb_values = [] # all my param values

        for k, v in exp_params.iteritems():
            comb_options.append(k)
            comb_values.append(v)
        comb_values = combiner(comb_values)

        # if we filter the todo-list, remove some configs
        num = len(comb_values)
        for i in xrange(num-1, -1, -1):
            tmpcv = comb_values[i]
            matches = True
            for k, vals in limit_to.iteritems():
                if not str(tmpcv[comb_options.index(k)]) in vals:
                    matches = False
            if not matches:
                comb_values.pop(i)

        return comb_options, comb_values

    def incrTo(val, highest):
        val += 1
        if val == highest+1:
            val = 1
        return val

    def decrTo(val, highest):
        val -= 1
        if val == 0:
            val = highest
        return val

    def make_dir(srv, cpu):
        '''make a new dir in the conf directory (if it exists, delete it)'''
        pdir = os.path.join(expfolder, 'conf', str(srv), str(cpu))
        if os.path.exists(pdir):
            rmtree(pdir)
        os.makedirs(pdir)
        return pdir

    def writeopt((opt, isint, sec), tosub=True):
        ''' helper function to copy values in conf file from meta and control section '''
        right_conf = exp_conf.has_option(sec, opt) and exp_conf or conf
        getter = isint and getattr(right_conf, 'getint') or getattr(right_conf, 'get')
        target_conf = tosub and sub_conf or main_conf
        target_conf.write('%s:%s\n' % (opt, getter(sec, opt)))


    # ---------------------------------------------------------------------------------------------
    # get parameters from subexperiments: combine them into our normal params
    default_params = {}
    for param in conf.options('params'):
        default_params[param] = [v.strip() for v in conf.get('params', param).split(',')]
    experiments = {'': default_params}
    if 'experiments' in conf.sections() and conf.get('experiments', 'configs') != '':
        experiments = {}
        for ex in conf.get('experiments', 'configs').split(','):
            ex = ex.strip()
            experiments[ex] = default_params.copy()
            exp_conf = ConfigParser()
            exp_conf_name = "%s/%s.conf" % (expfolder, ex)
            if not os.path.exists(exp_conf_name):
                print "[Nicessa] Error: Can't find %s !" % exp_conf_name
                sys.exit()
            exp_conf.read(exp_conf_name)
            for param in exp_conf.options('params'):
                experiments[ex][param] = [v.strip() for v in exp_conf.get('params', param).split(',')]

    # ---------------------------------------------------------------------------------------------
    # find out how many confs each host should do for each experiment
    hosts = utils.num_hosts(expfolder)
    cpus_per_host = utils.cpus_per_host(expfolder)
    # this is the host we currently use, we don't reset this between experiments to get a fair distribution
    host = 0
    num_per_hosts = range(len(experiments.keys()))
    for n in range(len(num_per_hosts)):
        num_per_hosts[n] = dict.fromkeys(range(hosts), 0)
    unfulfilled = dict.fromkeys(range(hosts), 0)

    # these hold all parameter names and the different value configurations, per experiment
    comb_options = {} # param names
    comb_values = {} # param values

    for expname in experiments.keys():
        nums = num_per_hosts[experiments.keys().index(expname)]

        comb_options[expname], comb_values[expname] = get_options_values(experiments[expname], limit_to)
        confs = len(comb_values[expname])
        host = incrTo(host, hosts) # move to next host from where we left off
        if sum(cpus_per_host.values()) == 0:
            print "[Nicessa]: You have not configured any CPUs for me to use. Stopping Configuration ..."
            return
        while 1==1:
            available = min(int(cpus_per_host[host]), confs)
            # if earlier we gave the last host too few, let's even that out right now
            last_host = decrTo(host, hosts-1)
            last_exp = num_per_hosts[decrTo(experiments.keys().index(expname), len(experiments.keys())-1)]
            if unfulfilled[last_host] > 0:
                onlast = min(available, min(cpus_per_host[last_host], unfulfilled[last_host]))
                nums[last_host] += onlast
                confs -= onlast
                unfulfilled[last_host] -= onlast
                available = min(int(cpus_per_host[host]), confs)
                if confs <= 0: break
            if int(cpus_per_host[host]) > available:
                unfulfilled[host] += int(cpus_per_host[host]) - available
            nums[host-1] += available
            confs -= available
            if confs <= 0: break
            host = incrTo(host, hosts)

    # ---------------------------------------------------------------------------------------------
    # now write all the conf files

    for host in xrange(1, hosts+1):
        # find out how much each cpu should get (in a helper list, distribute excess one by one)
        load = 0
        for exp in num_per_hosts:
            load += exp[host-1]
        my_cpus = cpus_per_host[host]
        if my_cpus == 0:
            continue
        cpuloads = dict.fromkeys(xrange(1, my_cpus+1), load / my_cpus)
        excess = load % my_cpus
        if excess > 0:
            cpu = 1
            while excess > 0:
                cpuloads[cpu] += 1
                cpu = incrTo(cpu, my_cpus)
                excess -= 1
        for cpu in xrange(1, my_cpus+1):
            if cpuloads[cpu] > 0:
                # open a main conf
                prefix_dir = make_dir(host, cpu)
                main_conf_name = '%s/main.conf' % prefix_dir
                main_conf = open(main_conf_name, 'w')

                if conf.has_section('seeds'):
                    main_conf.write('\n[seeds]\n')
                    num_seeds = len(conf.items('seeds'))
                    for dat in [(str(opt), isint, 'seeds') for (opt, isint) in zip(range(1, num_seeds+1), [1 for _ in range(num_seeds)])]:
                        writeopt(dat, tosub=False)

            # write as many confs as cpuloads prescribes for this cpu
            for job in range(cpuloads[cpu]):
                expindex = 0
                expname = experiments.keys()[expindex]
                while len(comb_values[expname]) == 0:
                    expindex += 1
                    if expindex == len(experiments.keys()): break
                    expname = experiments.keys()[expindex]
                act_comb_values = comb_values[expname].pop()
                sub_name = "%s_" % expname
                for i in range(len(act_comb_values)):
                    sub_name += "%s%s" % (experiments[expname].keys()[i], act_comb_values[i])
                    if i < len(act_comb_values)-1:
                        sub_name += "_"
                sub_conf = open('%s/%s.conf' % (prefix_dir, sub_name), 'w')

                # these sections settings can be overwritten per experiment
                exp_conf = ConfigParser(); exp_conf.read("%s/%s.conf" % (expfolder, expname))
                sub_conf.write('[meta]\n')
                for dat in [(opt, isint, 'meta') for (opt, isint) in [('name', 0), ('maintainer', 0)]]:
                    writeopt(dat)
                sub_conf.write('[control]\n')
                for dat in [(opt, isint, 'control') for (opt, isint) in [('runs', 1), ('executable', 0)]]:
                    writeopt(dat)
                if more:
                    sub_conf.write('start_run:%d\n' % (utils.runs_in_folder(expfolder, sub_name) + 1))
                sub_conf.write('\n')

                sub_conf.write('[params]\n')
                for i in range(len(act_comb_values)):
                    sub_conf.write('%s:%s\n' % (comb_options[expname][i], act_comb_values[i]))

                sub_conf.flush()
                sub_conf.close()

                # mention this sub-conf in the main-conf of this cpu
                main_conf.write('\n')
                main_conf.write('[%s]\n' % sub_name)
                main_conf.write('config_file = %s/%s.conf\n' % (prefix_dir, sub_name))
                main_conf.flush()

            main_conf.close()

