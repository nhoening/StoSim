#!/usr/bin/python

'''
harvester
==========

This module helps to collect certain files and values from the whole data set,
based on search criteria.
Main functions to use are collect_files and collect_values.
'''

import os
import sys


# ---- main functions ----

def collect_files(searches, filepath, target_dir):
    ''' For each search, collect all .log-files from the data directories that matches the criteria.
        Create a subdir for each search in target_dir where the .log-files go, numbered from 1 to n.

        :param dict searches: a dict, where the keys are names of searches and values
                  are lists of key-value tuples which dirnames should match
        :param string filepath: path to data directories
        :param string target_dir: directory where the subdirs should go
        :returns: a list with searches that didn't match any folders
   '''
    failed = []

    for s in searches.keys():
        if not os.path.exists('%s/%s' % (target_dir, s)):
            os.makedirs('%s/%s' % (target_dir, s))

        foldernames = [fn for fn in os.listdir(filepath) if matches(fn, searches[s])]
        if len(foldernames) == 0:
            failed.append(s)

        copied_files = 0
        for fon in foldernames:
            filenames = [fin for fin in os.listdir('%s/%s' % (filepath, fon)) if fin.endswith('.csv')]
            for fin in filenames:
                copied_files += 1
                os.system('cp %s/%s/%s %s/%s/%d.log' % (filepath, fon, fin, target_dir, s, copied_files))
    return failed


def collect_values(filepath, outfile_name, cols=[], selector='all'):
    '''
    Collect specific x/y values from a bunch of .log files (to be found via the filepath)
    and write them into a new file.

    :param string filepath: path to the .log files
    :param string outfile_name: path and name of file to write into
    :param list cols: columns to select, at least one,
                      we consider the first as x, the second as y
    :param selector: method to specify how to choose lines from the data files
                     one of ['all', 'last', 'max_x', 'max_y', 'min_x', 'min_y']
    TODO: how to pass custom selectors?
    '''
    assert(selector in ['all', 'last', 'max_x', 'max_y', 'min_x', 'min_y'])
    import harvester
    selector = harvester.__getattribute__('select_%s' % selector)
    vals = []
    files = [f for f in os.listdir(filepath) if f.endswith('.log')]
    for f in files:
        tmp = open('%s/%s' % (filepath, f), 'r')
        vals.extend(selector(tmp, cols))
    out = open(outfile_name, 'w')
    for v in vals:
        out.write('%s' % str(v))
    out.close()



# ---- selectors ----

def select_all(filep, cols):
    ''' select column values of all lines

    :param file filep: pointer to data file
    :param list cols: list of column indices from which to collect
    :returns: string with lines
    '''
    s = ''
    for line in [l for l in filep.readlines() if not l.startswith('#')]:
        s += '%s\n' % ' '.join([line.split(',')[cols[i]-1].strip() for i in range(len(cols))])
    return s


def select_last(filep, cols):
    ''' :returns: a string with the last values from this file and columns
        TODO: custom delimiter

    :param file filep: pointer to data file
    :param list cols: list of column indices from which to collect
    :returns: string with line
    '''
    lines = [l for l in filep.readlines() if not l.startswith('#')]
    last_line = lines[len(lines)-1].split(',')
    return '%s\n' % ' '.join([last_line[cols[i]-1].strip() for i in range(len(cols))])


def select_max_x(filep, cols):
    ''':returns: a string with the values from the line with maximal x-value

    :param file filep: pointer to data file
    :param list cols: list of column indices from which to collect
    '''
    return extreme(filep, cols, sel=max, by=0)


def select_max_y(filep, cols):
    ''':returns: a string with the values from the line with maximal y-value

    :param file filep: pointer to data file
    :param list cols: list of column indices from which to collect
    '''
    return extreme(filep, cols, sel=max, by=1)


def select_min_x(filep, cols):
    ''':returns: a string with the values from the line with minimal x-value

    :param file filep: pointer to data file
    :param list cols: list of column indices from which to collect
    '''
    return extreme(filep, cols, sel=min, by=0)


def select_min_y(filep, cols):
    ''':returns: a string with the values from the line with minimal y-value

    :param file filep: pointer to data file
    :param list cols: list of column indices from which to collect
    '''
    return extreme(filep, cols, sel=min, by=1)


# ---- helpers ----

def matches(string, search):
    ''':returns: True if string contains all key/value pairs in search s, False otherwise
       :params string string: string to search in
       :params dict search: key-values in this dict are the search
    '''
    for k, v in search:
        if string.rfind('%s%s' % (k, v)) < 0:
            return False
    return True


def extreme(filep, cols, sel=max, by=0):
    ''' Helper for selectors. Gets lines with maximal or minimal value,
        looking for those values in a column of choice.

    :param file filep: pointer to data file
    :param list cols: list of column indices from which to collect
    :param function sel: function to selct value from a list, max or min
    :param int by: the column of choice, default 0

    :returns: a string with the values from the line with minimal y-value
    '''
    assert(sel in [max, min])
    assert(by in [0,1])
    lines = [l for l in filep.readlines() if not l.startswith('#')]
    vals = [float(v.split(',')[cols[by]-1]) for v in lines]
    line = lines[vals.index(sel(vals))].split(',')
    return '%s\n' % ' '.join([line[cols[i]-1].strip() for i in range(len(cols))])


