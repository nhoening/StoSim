import pytest
import os
from shutil import rmtree
from subprocess import call

from stosim.sim.commands import snapshot

def test_snapshots():
    edir = 'examples/basic'
    snapdir = 'stosim-snapshots'
    if os.path.exists('{}/{}'.format(edir, snapdir)):
        rmtree('{}/{}'.format(edir, snapdir))
    snapshot(edir, identifier='FIRST')
    assert(os.path.exists('{}/{}'.format(edir, snapdir)))
    sdir_list = os.listdir('{}/{}'.format(edir, snapdir))
    assert(len(sdir_list) == 1)
    s1 = '{}/{}/{}'.format(edir, snapdir, sdir_list[0])
    assert(s1.endswith('FIRST'))
    assert(len(os.listdir(edir)) - 1 == len(os.listdir(s1)))
    snapshot(edir, identifier='SECOND')
    sdir_list = os.listdir('{}/{}'.format(edir, snapdir))
    sdir_list.sort()
    s2 = '{}/{}/{}'.format(edir, snapdir, sdir_list[1])
    assert(s1 != s2)
    for f1, f2 in zip(os.listdir(s1), os.listdir(s2)):
        assert(f1 == f2)  # same content
        call('touch {}/stosim.conf'.format(s1), shell=True)
        assert(os.path.getmtime('{}/stosim.conf'.format(s1)) !=\
               os.path.getmtime('{}/stosim.conf'.format(edir)))
        assert(os.path.getmtime('{}/stosim.conf'.format(s1)) ==\
               os.path.getmtime('{}/stosim.conf'.format(s2)))
