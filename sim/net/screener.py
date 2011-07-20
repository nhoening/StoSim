#!/usr/bin/python
'''
screener
========
'''

import sys
import os
from subprocess import Popen
import time
import os.path as osp


def run(screen_name, command, abs_path):
    '''
    Runs a command in a background screen. If necessary, it retries 10 times if the screen didn't start.
    It ecpects a name for the screen and the command as arguments

    :params string screen_name: Name for the screen (to be identifiable)
    :params string command: Command to run in this screen
    :params string abs_path: absolute path to this module
    '''
    command = "touch %s_started;%s" % (screen_name, command)

    f = open('screenrcs/%s.rc' % screen_name, 'w')
    f.write('shell bash\n')
    f.write('deflog on\n')
    f.write('logfile screenlogs/%s.log\n' % screen_name)
    f.close()

    counter = 1
    while counter < 10:
        Popen("%s/bgscreen %s '%s'" % (abs_path, screen_name, command), shell=True).wait()
        time.sleep(1)
        if os.path.exists("%s_started" % screen_name):
            print "[Nicessa] I ran %s on screen %s ..." % (command, screen_name)
            os.remove("%s_started" % screen_name)
            counter = 10
        else:
            print 'trying opnieuw'
            Popen("kill `ps aux | awk '/%s/{print $2}'`;" % (screen_name), shell=True).wait()
            counter += 1
    print "done."


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], osp.join(osp.dirname(osp.abspath(__file__))))
