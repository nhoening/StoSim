#!/usr/bin/python

'''
compressor
==========

Compresses data (e.g. averaging)
'''

import os
# cannot get this to work on my ibook :-(
# import numpy
import math # so I'll compute by hand


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

    # for each row, write X, mean and STD in target file
    hasMoreRows = True
    while hasMoreRows:
        vals = []
        x = None
        # get values from each file
        file_index = 0
        while file_index < numFiles:
            s = of[file_index].readline().strip().split(delim)
            #if s[0].startswith("#") or s[0].startswith('time_stamp'): continue
            file_index += 1
            if s == ['']: hasMoreRows = False # now no file is looked at no more
            else:
                if not (s[0].startswith("#") or s[0].startswith('time_stamp')):
                    try:
                        vals.append(float(s[int(yCol)-1])) # this might happen when file is corrupted
                        #assert(x is None or x == s[xCol-1]) # x values need to be the same in all files
                        x = s[xCol-1]
                    except Exception, e:
                        print "ERROR"

        if hasMoreRows and len(vals)>0:
            # mean
            sum = 0.0
            for v in vals: sum += v
            mean = sum / float(len(vals))
            # sample standard deviation
            std = 0.0
            for v in vals: std += math.pow(v - mean, 2)
            std /= len(vals)
            std = math.sqrt(std)
            std /= math.sqrt(len(vals)) # standard error: divide by sample size
            out.write('%s %f %f\n' % (str(x), mean, std))

    out.close()
    for i in xrange(numFiles):
        of[i].close()

