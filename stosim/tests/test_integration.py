import pytest
import os
from shutil import rmtree

from stosim.sim.commands import run, make_plots, run_ttests, prepare_folders_and_jobs


def file_lc(fname):
    ''' count lines in a file '''
    i = -1
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


class TestBasicExample(object):
    '''
    Run the basic example and check that results exist in jobs, data and plots
    '''
    edir = 'examples/basic'
    num_settings = 1
    num_runs = 5
    result_lines = 500
    plots = ['randomwalk_plot_1.pdf']

    @pytest.fixture(scope='module', autouse=True)
    def run_it(self):
        for d in ('jobs', 'data', 'plots'):
            if os.path.exists('{}/{}'.format(self.edir, d)):
                rmtree('{}/{}'.format(self.edir, d))
        prepare_folders_and_jobs(self.edir)
        run(self.edir)
        make_plots(self.edir)
        run_ttests(self.edir)

    def test_jobs(self):
        assert(os.path.exists('{}/jobs'.format(self.edir)))
        assert(len(os.listdir('{}/jobs'.format(self.edir)))\
                == self.num_runs * self.num_settings)

    def test_data(self):
        assert(os.path.exists('{}/data'.format(self.edir)))
        for dd in os.listdir('{}/data'.format(self.edir)):
            # test existence of files
            data = os.listdir('{}/data/{}'.format(self.edir, dd))
            data.sort()
            exp_data = ['log' + str(i) + '.dat'\
                            for i in range(1, self.num_runs + 1)]
            data.sort()
            exp_data.sort()
            assert(data == exp_data)
            # test existence of content
            for log in os.listdir('{}/data/{}'.format(self.edir, dd)):
                assert(file_lc('{}/data/{}/{}'.format(self.edir, dd, log))\
                       == self.result_lines)

    def test_plots(self):
        assert(os.path.exists('{}/plots'.format(self.edir)))
        assert(os.listdir('{}/plots'.format(self.edir)) == self.plots)


class TestSubsimExample(TestBasicExample):

    edir = 'examples/subsim'
    num_settings = 12
    num_runs = 20
    result_lines = 201
    plots = ['simulation1_cooperative.pdf','simulation1_non-cooperative.pdf',
             'simulation1_payoff.pdf', 'simulation2_cooperative.pdf',
             'simulation2_non-cooperative.pdf', 'simulation2_payoff.pdf']


class TestStochasticExample(TestSubsimExample):

    edir = 'examples/stochastic'
    num_runs = 10
