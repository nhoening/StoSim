'''
remote
======
Code to realise runnning simulations remotely
All remote communication is done via SSH with the help of paramiko
'''

import sys
import os
import os.path as osp
import time
from subprocess import Popen
# ignore deprecation warnings that paramiko currently delivers
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
import paramiko
import scp

from sim import utils


def ssh(client, cmd):
    '''
    Run cmd on remote client (retry if connection fails), show errors (if we care about them)

    :params paramiko.SSHClient client:
    :params string cmd:
    :returns: stdout from host (minus some things we consider irrelevant)
    '''
    done = False
    while not done:
        try:
            stdin, stdout, stderr = client.exec_command(cmd)
            done = True
        except:
           time.sleep(4)
    err = stderr.read()
    dontcare_snippets = ['xset:', 'cannot remove', 'cannot access finished_*',\
                         'are the same file', 'finished_*: No such']
    err_out = ""
    for e_line in err.split('\n'):
        yell_it = True
        for s in dontcare_snippets:
            if s in e_line:
                yell_it = False
        if yell_it and e_line != "":
            err_out += '%s\n' % e_line
    if err_out != "":
        print "[Nicessa] Error while doing stuff on server: %s" % (err_out)
    return "[Nicessa] Log from remotely executing %s:\n\n\n%s" % (cmd, stdout.read())


def run_remotely(simfolder, conf):
    '''
    Runs simulation as it was setup on remote hosts

    :param string simfolder: relative path to simfolder
    :param ConfigParser conf: main config
    '''
    folder = simfolder
    remote_conf = utils.get_host_conf(simfolder)
    num_hosts = utils.num_hosts(simfolder)

    for host in xrange(1, num_hosts+1):
        ssh_client = _get_ssh_client(remote_conf, host)
        if not remote_conf.has_section("host%i" % host):
            print "[Nicessa] Server %d is not configured!" % host
            return

        path = remote_conf.get("host%i" % host, "path")
        # ------------- clean host (we want to be sure to use fresh code)
        # do this on all hosts before anything is run (e.g. they could operate on the same home dir)
        cleaning = "mkdir -p %s/%s;" % (path, folder)
        togo = "data conf nicessa.conf %s bgscreen screener.py starter.py _nicessa_bundle.tar.gz" \
                % (conf.get('control', 'executable'))
        if remote_conf.has_option('code', 'files'):
            for f in [f for f in remote_conf.get('code', 'files').split(',') if f is not ""]:
                togo += " %s/%s " % (simfolder, f.strip())
        if remote_conf.has_option('code', 'folders'):
            for f in [f for f in remote_conf.get('code', 'folders').split(',') if f is not ""]:
                togo += " %s/%s " % (simfolder, f.strip())
        cleaning += "cd %s/%s; rm -r %s;" % (path, folder, togo)
        # make fresh dirs to config and log screens
        cleaning += 'mkdir -p screenrcs; rm -r screenrcs/*; mkdir -p screenlogs; rm -r screenlogs/*;'
        # clean old states, too - never know how the last run was finished (e.g. Ctrl-C)
        cleaning += clean_states(simfolder, conf, host)
        ssh(ssh_client, cleaning)

    used_hosts = 0
    cpus_per_host = utils.cpus_per_host(simfolder)
    for host in xrange(1, num_hosts+1):
        # -------------  initialize each host
        # don't proceed if a host doesn't have work to do (TODO: maybe also don't clean before?)
        host_has_work = False
        if osp.exists("%s/conf/%d" % (simfolder, host)):
            host_has_work = True
            used_hosts += 1
        if not host_has_work:
            continue

        # ------------- start screen(s) on all of them
        # let him run the batch for this host in a background screen (for each simulation we might have)
        # TODO: remote works only with subsimulations right now? We should fix that
        screening = ""
        for cpu in xrange(1, cpus_per_host[host]+1):
            if osp.exists("%s/conf/%d/%d" % (simfolder, host, cpu)):
                screening += "rm %s/finished_%i_%i; ./%s/screener.py screen_host_%i_cpu_%i './%s/starter.py %s %i %i; touch %s/finished_%i_%i;exit;'; " \
                    % (folder, host, cpu, folder, host, cpu, folder, folder, host, cpu, folder, host, cpu)

        #  --- local file shuffling
        if not simfolder == ".":
            os.chdir(simfolder)

        # all host-side screen calls go in a script file, so screener.py can quietly make sure they all start without me waiting
        cmd = open("cmd_%d" % host, 'w')
        cmd.write(screening)
        cmd.flush(); cmd.close()
        Popen("chmod +x cmd_%d;" % host, shell=True).wait();
        needed = " cmd_%d" % host

        # send everything needed of the simulation to run batches to the host in one go
        needed += " conf"
        needed += " nicessa.conf"
        needed += " %s" % (conf.get('control', 'executable'))
        if remote_conf.has_option('code', 'files'):
            for f in [f for f in remote_conf.get('code', 'files').split(',') if f is not ""]:
                needed += " %s" %f
        if remote_conf.has_option('code', 'folders'):
            for f in [f for f in remote_conf.get('code', 'folders').split(',') if f is not ""]:
                needed += " %s" %f
        # also some nicessa files
        pth = osp.join(osp.dirname(osp.abspath(__file__)))
        copied_here = []
        for filename in ['bgscreen','screener.py','starter.py']:
            Popen("cp %s/%s ." % (pth, filename), shell=True).wait()
            copied_here.append(filename)
            needed += " %s" % filename.split('/')[-1:][0]

        # put all we need in a tar.gz archive
        Popen("tar -cf _nicessa_bundle.tar %s; gzip -f _nicessa_bundle.tar;" % (needed), shell=True).wait()

        if not simfolder == ".":
            for _ in simfolder.split("/"):
                os.chdir('..')
        # --- end local file shuffling

        # ------------ now we actually connect and do all these things online
        initializing = "cd %s/%s; tar -zxf _nicessa_bundle.tar.gz; cd; cd %s;" % (path, folder, path)

        ssh_client = _get_ssh_client(remote_conf, host)
        try:
            print "[Nicessa] Running code on %s" %  remote_conf.get("host%i" % host, "name")
            scp_client = scp.SCPClient(ssh_client._transport)
            scp_client.put("%s/_nicessa_bundle.tar.gz" % simfolder, remote_path="%s/%s" % (path, folder))
            time.sleep(2)
            log = open("log%d" % host, 'w')
            log.write(ssh(ssh_client, "%s mv %s/cmd_%d .; ./cmd_%d; rm cmd_%d;" % (initializing, folder, host, host, host)))
            log.flush()
            log.close()
        except scp.SCPException, e:
            print e
        ssh_client.close()

        # ------------ clean locally
        os.remove("%s/_nicessa_bundle.tar.gz" % simfolder)
        os.remove("%s/cmd_%d" % (simfolder, host))
        for c in copied_here:
            os.remove("%s/%s" % (simfolder, c))

    print "[Nicessa] deployed simulation on %i host(s)" % (used_hosts)


def check(simfolder):
    '''
    Performs a check to find out which portions of the exeriment are already done.
    For this, it looks at the marker files when a job is done.
    Prints out results.

    :param string simfolder: relative path to simfolder
    '''
    conf = utils.get_main_conf(simfolder)
    hosts = utils.num_hosts(simfolder)
    cpus_per_host = utils.cpus_per_host(simfolder)
    finished = dict.fromkeys(xrange(1, hosts+1))
    running = dict.fromkeys(xrange(1, hosts+1))
    for host in xrange(1, hosts+1):
        finished[host] = []
        running[host] = []
    remote_conf = utils.get_host_conf(simfolder)

    print "[Nicessa] Checking hosts: ",
    sys.stdout.flush()
    for host in xrange(1, hosts+1):
        hostname = remote_conf.get("host%i" % host, "name")
        print "%s (host-nr:%d, cpus:%d)  " % (hostname, host, cpus_per_host[host]),
        sys.stdout.flush()
        ssh_client = _get_ssh_client(remote_conf, host)
        if ssh_client:
            path = remote_conf.get("host%i" % host, "path")
            fin = ssh(ssh_client, 'cd %s/%s; ls finished_*;' % (path, simfolder))
            run = ssh(ssh_client, 'screen -ls;')
            for cpu in xrange(1, cpus_per_host[host]+1):
                if "finished_%d_%d" % (host, cpu) in fin:
                    finished[host].append(cpu)
                if "screen_host_%d_cpu_%d" % (host, cpu) in run:
                    running[host].append(cpu)
                if "No sockets found" in run:
                    print "No sockets found on host %s..." % hostname
    print
    print "[Nicessa] Finished cpus:"
    for host in finished.keys():
        print " %.18s:\t%s" % (remote_conf.get("host%i" % host, "name").ljust(12), str(finished[host]))
    print "[Nicessa] Still running cpus:"
    for host in running.keys():
        print " %.18s:\t%s" % (remote_conf.get("host%i" % host, "name").ljust(12), str(running[host]))


def get_results(simfolder, do_wait=True):
    '''
    Copies result logs from the remote host(s) if they are all available for the whole job.

    :param string simfolder: relative path to simfolder
    :param boolean do_wait: True if regular checks should be done until all data is available (default is True)
    '''
    print '*' * 80
    print "[Nicessa] getting results ... "
    print "[Nicessa] This may take a while, depending on your simulation. I'll tell you when I got everything from a host."

    conf = utils.get_main_conf(simfolder)
    remote_conf = utils.get_host_conf(simfolder)
    cpus_per_host = utils.cpus_per_host(simfolder)
    hosts_done = dict.fromkeys(xrange(1, utils.num_hosts(simfolder)+1), False)
    all_done = False
    if remote_conf.has_option('communication', 'wait'):
        if do_wait:
            waiting = remote_conf.getint('communication', 'wait')
            print "[Nicessa] waiting for %d seconds ... " % waiting
            time.sleep(waiting)
    if remote_conf.has_option('communication', 'check'):
        check_interval = remote_conf.getint('communication', 'check')
    else:
        check_interval = 10
    first_time_done = False

    while not all_done:
        for host in hosts_done.keys():
            if not hosts_done[host]:
                hostname = remote_conf.get("host%i" % host, "name")
                if first_time_done:
                    print ".",
                ssh_client = _get_ssh_client(remote_conf, host)
                if ssh_client:
                    try:
                        path = remote_conf.get("host%i" % host, "path")
                        # check for status by looking for the marker files this host should generate
                        res = ssh(ssh_client, 'cd %s/%s; ls' % (path, simfolder))
                        # TODO: this is no good when we get the results on a different computer than we started from
                        #relevant_subsims = [subsim for subsim in utils.get_simulation_names(conf) if osp.exists("%s/conf/%s/%s" % (simfolder, subsim, host))]
                        if cpus_per_host[host] == 0:
                            hosts_done[host] = True
                        elif 'data' in res and reduce(lambda x, y: x and y, \
                                             map(res.__contains__, ["finished_%s_%i" % (host, cpu) for cpu in xrange(1, cpus_per_host[host]+1)])):
                            scp_client = scp.SCPClient(ssh_client._transport)
                            try:
                                print "[Nicessa] copying data from %s ... " % hostname ,
                                ssh(ssh_client, 'cd %s/%s; tar -cf data_%d.tar data/*; gzip -f data_%d.tar;' % (path, simfolder, host, host))
                                time.sleep(2)
                                scp_client.get("%s/%s/data_%d.tar.gz" % (path, simfolder, host), local_path='%s' % simfolder)
                                os.chdir(simfolder)
                                Popen("tar -zxf data_%d.tar.gz; rm data_%d.tar.gz" % (host, host), shell=True).wait()
                                if not simfolder == ".":
                                    for _ in simfolder.split("/"):
                                        os.chdir('..')
                            except OSError, e:
                                print e
                            hosts_done[host] = True
                            print "done."
                            ssh(ssh_client, 'cd %s/%s; %s' % (path, simfolder, clean_states(simfolder, conf, host)))
                    except Exception, e:
                        print e
                    ssh_client.close()
                else:
                    print "cannot connect to %s " % host
                    pass # keep on trying
                    #hosts_done[host] = True # can't connect, so don't keep on trying
        print "_",
        sys.stdout.flush()
        # all done now?
        all_done = True
        for done in hosts_done.values():
            all_done = all_done and done
        if not first_time_done and not all_done:
            print "[Nicessa] now checking every %d seconds ... " % check_interval
            first_time_done = True
        if not all_done:
            time.sleep(check_interval)
    print "[Nicessa] Got all results."
    print '*' * 80
    print;


def show_screen(simfolder, host, cpu, lines=50):
    '''
    Show the screen log of the screen running on a specific host and cpu.

    :param string simfolder: relative path to simfolder
    :param int host: index of host
    :param int cpu: index of cpu
    '''
    screen_name = 'screen_host_%i_cpu_%i' % (host, cpu)
    remote_conf = utils.get_host_conf(simfolder)
    host_name = remote_conf.get("host%i" % host, "name")
    ssh_client = _get_ssh_client(remote_conf, host)

    running = ssh(ssh_client, 'screen -ls;')
    if not screen_name in running:
        print '[Nicessa] No screen for cpu %i on %s is running at the moment.' % (cpu, host_name)
        return

    scp_client = scp.SCPClient(ssh_client._transport)
    path = remote_conf.get("host%i" % host, "path")
    print "[Nicessa] getting screen log from %s ... " % host_name
    try:
        scp_client.get("%s/%s/screenlogs/%s.log" % (path, simfolder, screen_name), local_path='%s' % simfolder)
    except scp.SCPException, e:
        print e
    local_file_name = '%s/%s.log' % (simfolder, screen_name)
    if os.path.exists(local_file_name):
        f = open(local_file_name, 'r')
        all_lines = f.readlines()
        f.close()
        os.remove('%s/%s.log' % (simfolder, screen_name))
        print '************* Begin Screen Content ********************'
        for line in all_lines[-1 * lines:]:
            print line,
        print '************* End Screen Content **********************'
    else:
        print '[Nicessa] Couldn\'t download the screen log for cpu %i on %s.' % (cpu, host_name)


def _get_ssh_client(remote_conf, host):
    '''
    make an SSH client and connect it

    :param ConfigParser remote_conf: host configuration
    :param int host: index of host
    :returns: paramiko.SSHClient
    '''
    usr = remote_conf.get("host%i" % host, "user")
    hostname = remote_conf.get("host%i" % host, "name")
    passwd = remote_conf.get("host%i" % host, "passwd")

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.connect(hostname, username=usr, password=passwd)
    except:
        print "[Nicessa] WARNING: Could not connect to host %s. Is it a known host (look in .ssh/known_hosts)? Is the password correct?" % hostname
        return None
    return ssh_client


def clean_states(simfolder, conf, host):
    '''
    Build commands which remove traces of any (former) Nicessa activity on one host:
    clean running screens and files that are used to indicate states.
    For files, we assume to be located in the data dir Nicessa uses in that host.

    :param string simfolder: relative path to simfolder
    :param ConfigParser remote_conf: host configuration
    :param int host: index of host
    :returns: a string with all ``rm`` and ``kill`` commands
    '''
    clean = ""
    clean += "rm data_%d.tar.gz;" % host
    clean += "rm cmd_%d;" % host
    # clean up marker files
    for cpu in utils.cpus_per_host(simfolder):
        clean += 'rm finished_%i_%i;' % (host, cpu)
    # kill old screens by name
    pattern = '|'.join(["screen_host_%i_cpu_%i" % (host, cpu) for cpu in range(1, utils.cpus_per_host(simfolder)[host]+1)])
    clean += "kill `ps aux | awk '/%s/{print $2}'`;" % pattern
    return clean

