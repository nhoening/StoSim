#!/usr/bin/python

'''
job_creator
=====

This module sets up the stage - with it, you can make a configuration file
for each mix of parameter settings (for each job) that needs to be run.
'''

import sys
import os
from ConfigParser import ConfigParser

import utils



def create(main_conf, simfolder, limit_to={}, more=False):
    """
    Writes a conf file for each run that the parameters in conf suggest.

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

    def mk_option((opt, isint, sec), sim_conf):
        ''' helper function to copy values in conf file from meta and control section '''
        from_conf = sim_conf.has_option(sec, opt) and sim_conf or main_conf
        getter = isint and getattr(from_conf, 'getint') or getattr(from_conf, 'get')
        return '{}:{}\n'.format(opt, getter(sec, opt))

    def write_job(values, sim='', run=1):
        '''
        Write a job conf with these values for this sim
        '''
        job_name = "sim{}_".format(sim)
        for i in range(len(values)):
            job_name += "{}{}".format(options[i], values[i])
            if i < len(values) - 1:
                job_name += "_"
        job_conf_filename = '{}/jobs/{}_run{}.conf'.format(simfolder, job_name, run)
        job_conf = open(job_conf_filename, 'w')

        if more:
            run += utils.runs_in_folder(simfolder, job_name)

        # these meta sections settings are tricky - they might be overwritten 
        # per simulation and we might want to start where we left off
        sim_conf = ConfigParser(); sim_conf.read("%s/%s.conf" % (simfolder, sim))
        job_conf.write('[meta]\n')
        for dat in [(opt, isint, 'meta') for (opt, isint) in [('name', 0), ('maintainer', 0)]]:
            job_conf.write(mk_option(dat, sim_conf))

        job_conf.write('\n[control]\n')
        exe = mk_option(('executable', 0, 'control'), sim_conf)
        exe = 'executable: {}/{}\n'.format(os.path.abspath(simfolder), exe.split(':')[1].strip().strip('./'))
        job_conf.write(exe) 
        logfile = '{}/data/{}/log{}.dat'.format(simfolder, job_name, run)
        if not os.path.exists('{}/data/{}'.format(simfolder, job_name)):
            os.mkdir('{}/data/{}'.format(simfolder, job_name))
        job_conf.write('logfile: {}\n'.format(logfile))
        if main_conf.has_option('seeds', str(run)):
            seed = main_conf.get('seeds', str(run)) 
            job_conf.write('seed:{}\n'.format(seed)) 
        job_conf.write('\n')

        # write param values
        job_conf.write('[params]\n')
        for i in range(len(values)):
            job_conf.write('{}:{}\n'.format(options[i], values[i]))

        job_conf.flush()
        job_conf.close()

        scheduler=utils.get_scheduler(simfolder)
        if scheduler == 'pbs':
            pbs_job = '''# Shell for the job:
#PBS -S /bin/bash
# request 1 node, {cores} core(s)
#PBS -lnodes=1:cores{cores}:ppn={ppn}
# job requires at most n hours wallclock time
#PBS -lwalltime={maxtime}

cd {path2sim}
{cmd} {jobconf}'''.format(cmd=main_conf.get('control', 'executable'), cores=8, # the PBS cluster I know only has 8,12&16 core machines
                          path2sim=os.path.abspath(simfolder), ppn=1, # processes per node, so far we assume there is only one
                          maxtime=utils.get_jobtime(simfolder), jobconf=job_conf_filename)
            pbs_job_file = open('{}/jobs/{}_run{}.pbs'.format(simfolder, job_name, run), 'w')
            pbs_job_file.write(pbs_job)
            pbs_job_file.close()

    # ---------------------------------------------------------------------------------------------
    # now let's get going

    # get parameters from subsimulations: combine them with our normal params
    default_params = {}
    for param in main_conf.options('params'):
        default_params[param] = [v.strip() for v in main_conf.get('params', param).split(',')]
    simulations = {'': default_params}
    if 'simulations' in main_conf.sections() and main_conf.get('simulations', 'configs') != '':
        simulations = {}
        for sim in main_conf.get('simulations', 'configs').split(','):
            sim = sim.strip()
            simulations[sim] = default_params.copy()
            sim_conf = ConfigParser()
            sim_job_name = "%s/%s.conf" % (simfolder, sim)
            if not os.path.exists(sim_job_name):
                print "[StoSim] Error: Can't find %s !" % sim_job_name
                sys.exit()
            sim_conf.read(sim_job_name)
            if sim_conf.has_section('params'):
                for param in sim_conf.options('params'):
                    simulations[sim][param] = [v.strip() for v in sim_conf.get('params', param).split(',')]

    # now write all the conf files, once for each simulation and once for each seed
    for sim in simulations:
        options, values = get_options_values(simulations[sim], limit_to)
        
        for _ in range(len(values)):
            # get a set of unique values 
            act_values = values.pop()
            runs = main_conf.getint('control', 'runs')
            for run in xrange(1, runs+1):
                write_job(act_values, sim=sim, run=run)
                
