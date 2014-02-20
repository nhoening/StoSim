import os
import pytest
import subprocess
from shutil import rmtree


class TestBasicExample(object):
    '''
    Run the basic example and check that results exist in jobs, data and plots
    '''
    edir = 'examples/basic'

    @pytest.fixture(scope='module')
    def run_it(self):
        for d in ('jobs', 'data', 'plots'):
            if os.path.exists('{}/{}'.format(self.edir, d)):
                rmtree('{}/{}'.format(self.edir, d))
        subprocess.call('stosim --folder {}'.format(self.edir), shell=True)

    def test_jobs(self, run_it):
        assert(os.path.exists('{}/jobs'.format(self.edir)))
        assert(len(os.listdir('{}/jobs'.format(self.edir))) == 5)

    def test_data(self, run_it):
        assert(os.path.exists('{}/data'.format(self.edir)))
        data = os.listdir('{}/data/sim_steps500'.format(self.edir))
        data.sort()
        assert(data == ['log' + str(i) + '.dat' for i in xrange(1, 6)])

    def test_plots(self, run_it):
        assert(os.path.exists('{}/plots'.format(self.edir)))
        assert(os.listdir('{}/plots'.format(self.edir)) == ['randomwalk_plot_1.pdf'])
