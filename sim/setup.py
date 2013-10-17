#!/usr/bin/python

'''
setup
=====
TODO: rename, to sthg like job_creator

This module sets up the stage - with it, you can make a configuration file
for each mix of parameter settings (for each job) that needs to be run.
'''

import sys
import os
from ConfigParser import ConfigParser
from shutil import rmtree

import utils



def create(conf, simfolder, limit_to={}, more=False):
    """
    Writes a conf file for each run that the parameters in conf suggest.
    Also divides all runs of an simulation in groups with a main conf each, to run on different hosts.

    :param ConfigParser conf: main configuration
    :param string simfolder: relative path to simfolder
    :param dict limit_to: dict of configuration settings we should limit to (default is an empty dict)
    :param boolean more: True if runs should be appended to existing data (default is False)
    """

    # these hold all parameter names and the different value configurations, per simulation
    #comb_options = [] # a list of param names
    #comb_values = []  # a list of lists with param values - one per job

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


    def get_options_values(sim_params, limit_to):
        '''
        :param dict sim_params: dict of configuration for one simulation
        :param dict limit_to: dict of configuration settings we should limit to
        :returns: a list of option names and lists of values to use in every possible combination in one simulation.
        '''
        # these hold all parameter names and the different value configurations, per simulation
        comb_options = [] # a list of param names
        comb_values = []  # a list of lists with param values - one per job

        for k, v in sim_params.iteritems():
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

    def write_option((opt, isint, sec), to_conf, sim_conf):
        ''' helper function to copy values in conf file from meta and control section '''
        from_conf = sim_conf.has_option(sec, opt) and sim_conf or conf
        getter = isint and getattr(from_conf, 'getint') or getattr(from_conf, 'get')
        to_conf.write('{}:{}\n'.format(opt, getter(sec, opt)))

    def write_job(otpions, values, sim=''):
        '''
        Write a job conf with these values for this sim
        '''
        # prepare a config file
        conf_name = "sim{}_".format(sim)
        for i in range(len(values)):
            conf_name += "{}{}".format(options[i], values[i])
            if i < len(values) - 1:
                conf_name += "_"
        job_conf = open('{}/jobs/{}.conf'.format(simfolder, conf_name), 'w')

        # these meta sections settings are tricky - they might be overwritten 
        # per simulation and we might want to start where we left off
        sim_conf = ConfigParser(); sim_conf.read("%s/%s.conf" % (simfolder, sim))
        job_conf.write('[meta]\n')
        for dat in [(opt, isint, 'meta') for (opt, isint) in [('name', 0), ('maintainer', 0)]]:
            if conf.has_option('meta', opt):
                write_option(dat, job_conf, sim_conf)
        job_conf.write('[control]\n')
        for dat in [(opt, isint, 'control') for (opt, isint) in [('runs', 1), ('executable', 0)]]:
            write_option(dat, job_conf, sim_conf)
        if more:
            job_conf.write('start_run:%d\n' % (utils.runs_in_folder(simfolder, conf_name) + 1))
        job_conf.write('\n')

        # write param values
        job_conf.write('[params]\n')
        for i in range(len(values)):
            job_conf.write('{}:{}\n'.format(options[i], values[i]))

        job_conf.flush()
        job_conf.close()


    # ---------------------------------------------------------------------------------------------
    # now let's get going

    # get parameters from subsimulations: combine them with our normal params
    default_params = {}
    for param in conf.options('params'):
        default_params[param] = [v.strip() for v in conf.get('params', param).split(',')]
    simulations = {'': default_params}
    if 'simulations' in conf.sections() and conf.get('simulations', 'configs') != '':
        simulations = {}
        for sim in conf.get('simulations', 'configs').split(','):
            sim = sim.strip()
            simulations[sim] = default_params.copy()
            sim_conf = ConfigParser()
            sim_conf_name = "%s/%s.conf" % (simfolder, sim)
            if not os.path.exists(sim_conf_name):
                print "[NICESSA] Error: Can't find %s !" % sim_conf_name
                sys.exit()
            sim_conf.read(sim_conf_name)
            if sim_conf.has_section('params'):
                for param in sim_conf.options('params'):
                    simulations[sim][param] = [v.strip() for v in sim_conf.get('params', param).split(',')]

    # now write all the conf files, once for each simulation and once for each seed
    for sim in simulations:
        options, values = get_options_values(simulations[sim], limit_to)
        
        if conf.has_section('seeds'):
            comb_options[sim].append('seed')
            simulations[sim]['seed'] = ''
        
        for _ in range(len(values)):
            # get a set of unique values 
            act_values = values.pop()
            if conf.has_section('seeds'):
                for index, seed in conf.items('seeds'): #TODO: only do for as many runs as requested, error if too few seeds
                    vals = [v for v in act_values]
                    vals.append(seed)
                    print len(vals), vals
                    write_job(options, vals, sim=sim)
            else:
                write_job(options, act_values, sim=sim)
