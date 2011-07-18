#!/usr/bin/python

'''
compressor
==========

Compresses data (e.g. averaging)
'''

import os
import math


def avg_stats(xCol, yCol, numFiles, filePrefix='', fileSuffix='', filePath='.', delim=' ', outName=None):
    '''
    This function can take several data files and transfer them into a file that is formatted
    ready to be plotted by gnuplot.
    It will average over the Y column (that you specify) and record the standard deviation.
    Data files should be named using an index starting by 1 and all have the same prefix and/or suffix arround that index.

    In gnuplot, you could then say "plot outName smooth unique with yerrorlines"

    :param int xCol: x column
    :param int yCol: y column
    :param int numFiles: the number of files to average over
    :param string filePrefix: prefix in filenames
    :param string fileSuffix: suffix in filenames
    :param string filePath: path to files
    :param string delim: delimiter used between columns
    :param string outName: Name of the result file, defaults to <filePrefix><yCol><fileSuffix>.out
    '''

    assert os.path.exists(filePath), 'File path %s does not exist' % filePath
    if len(filePath) > 1 and not filePath.endswith("/"): filePath += "/"
    if numFiles is None:
        numFiles = len([f for f in os.listdir(filePath) if f.endswith(fileSuffix) and f.startswith(filePrefix)])
    assert numFiles, 'numFiles is zero or not set'
    assert xCol, 'xCol is not set'
    assert yCol, 'yCol is not set'

    # open files
    of = list()
    for i in xrange(1, numFiles+1, 1):
        of.append(open(filePath + filePrefix + str(i) + fileSuffix, 'r'))
    if outName is None: outName = '%s%s%s%s.out' % (filePath, filePrefix, str(yCol), fileSuffix)
    out = open(outName, 'w')

    # we'll collect values in this dictionary
    d = {}

    # for each x, collect y
    hasMoreRows = True
    while hasMoreRows: # assuming all files have the same number fo rows!
        #x = None
        # get values from each file
        file_index = 0
        while file_index < numFiles:
            s = of[file_index].readline().strip().split(delim)
            #if s[0].startswith("#") or s[0].startswith('time_stamp'): continue
            file_index += 1
            if s == ['']: hasMoreRows = False # now no file is looked at no more
            else:
                if not (s[0].startswith("#") or s[0].startswith('time_stamp')):
                    x = s[xCol-1].strip()
                    # make sure d has a list for that x
                    if not d.has_key(x):
                        d[x] = []
                    try:
                        # we assume that y values are nueric! Also,other
                        # errors might happen here when file is corrupted
                        d[x].append(float(s[int(yCol)-1]))
                    except Exception, e:
                        print "ERROR"

    # compute mean and standard deviation and write to target file
    keys = d.keys()
    keys.sort()
    for x in keys:
        # mean
        sum = 0.0
        for y in d[x]: sum += y
        mean = sum / float(len(d[x]))
        # sample standard deviation
        std = 0.0
        for y in d[x]:
            std += math.pow(y - mean, 2)
        std /= len(d[x])
        std = math.sqrt(std)
        #std /= math.sqrt(len(d[x])) # this would give the standard error of the mean
        out.write('%s %f %f\n' % (str(x), mean, std))

    out.close()
    for i in xrange(numFiles):
        of[i].close()

