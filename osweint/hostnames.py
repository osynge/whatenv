import os
import time
import novaclient.v1_1.client as nvclient
from credentials import get_nova_creds
import uuid
import json
import sys
from environ import getenviromentvars
import optparse
import logging
import subprocess
from command_runner import Command
import time
from __version__ import version




def host_operation(addresses,cmd):
    log = logging.getLogger("host_operation")
    connected = set()
    retry = True
    retry_count = 0
    retry_max = 100
    lastdifference = addresses
    log.debug("check=%s" % (cmd))
    while retry:
        retry_count += 1
        log.debug("retry_count=%s" % (retry_count))
        diff_before_check = addresses.difference(connected)
        for address in diff_before_check:
            croc = Command(cmd % (address))
            rc,stdout,stderr = croc.run(timeout=10)
            if rc == 0:
                connected.add(address)
                continue
            time.sleep(1)
        diff_after_check = addresses.difference(connected)

        log.debug("diff_before_check=%s" % (diff_before_check))
        log.debug("diff_after_check=%s" % (diff_after_check))
        if len(diff_before_check) == 0:
            retry = False
        if len(diff_before_check) > len(diff_after_check):
            log.info("extending time out")
            retry_count = 0
        if retry_count > retry_max:
            log.error("time out=%s" % (retry_count))
            retry = False
    return connected

def pinghosts(addresses):
    return host_operation(addresses,"ping -c 1 %s")


def sshhosts(addresses):
    return host_operation(addresses,"ssh -o StrictHostKeyChecking=no root@%s echo")






def clean_ssh_hostname(intext):
    splittext = intext.split('\n')
    splittext.reverse()
    for line in splittext:
        if len(line) == 0:
            continue
        return line
    return ''


def update_instance_data(instace):
    addresses = set()
    for netwrok in instace['OS_NETWORKS']:
        address_list = instace['OS_NETWORKS'][netwrok]
        addresses = addresses.union(address_list)
    for address in addresses:
        subprocess.call(["ssh-keygen", "-R", address])
    hostname_short = set()
    for address in addresses:
        croc = Command("ssh -o StrictHostKeyChecking=no root@%s hostname" % (address))
        rc,stdout,stderr = croc.run(timeout=30)
        if rc != 0:
            continue
        hostname_short.add(clean_ssh_hostname(stdout))
    hostname_long = set()
    for address in addresses:
        croc = Command("ssh -o StrictHostKeyChecking=no root@%s hostname -f" % (address))
        rc,stdout,stderr = croc.run(timeout=30)
        if rc != 0:
            continue
        hostname_long.add(clean_ssh_hostname(stdout))
    hostname_short_connected = set()
    for hostname in hostname_short:
        subprocess.call(["ssh-keygen", "-R", hostname])
        croc = Command("ssh -o StrictHostKeyChecking=no root@%s echo" % (hostname))
        rc,stdout,stderr = croc.run(timeout=30)
        if rc != 0:
            continue
        hostname_short_connected.add(hostname)
    hostname_long_connected = set()
    for hostname in hostname_long:
        subprocess.call(["ssh-keygen", "-R", hostname])
        croc = Command("ssh -o StrictHostKeyChecking=no root@%s echo" % (hostname))
        rc,stdout,stderr = croc.run(timeout=30)
        if rc != 0:
            continue
        hostname_long_connected.add(hostname)

    output = dict(instace)
    output['VM_HOSTNAME'] = list(hostname_short.union(hostname_long))
    return output

def read_input(filename):
    f = open(filename)
    json_string = f.read()
    loadedfile = json.loads(json_string)
    return loadedfile

def process_actions(file_state):
    log = logging.getLogger("process_actions")
    output_data = read_input(file_state)
    log.debug("here")
    #print output_data
    # Get full list of addresses
    addresses = set()
    for instace in output_data:
        for netwrok in output_data[instace]['OS_NETWORKS']:
            address_list = output_data[instace]['OS_NETWORKS'][netwrok]
            for address in address_list:
                addresses.add(address)
    pinged = pinghosts(addresses)
    log.debug("pinged=%s" % ( pinged))
    # Remove all address from known hosts
    for address in pinged:
        subprocess.call(["ssh-keygen", "-R", address])
    # check all addresses can be connected to.
    connected = sshhosts(pinged)
    log.debug("connected=%s" % ( connected))

    for instace in output_data:
        output = update_instance_data(output_data[instace])
        output_data[instace] = output
    #output_data.update(booted)
    f = open(file_state, 'w')
    json.dump(output_data, f, sort_keys=True, indent=4)
    #print json.dumps(output_data, sort_keys=True, indent=4)


def main():

    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logcfg', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-v', '--verbose', action ='count',help='Change global log level, increasing log output.', metavar='LOGFILE')
    p.add_option('-q', '--quiet', action ='count',help='Change global log level, decreasing log output.', metavar='LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Configuration file.', metavar='CFG_FILE')
    p.add_option('--state', action ='store',help='State file')
    p.add_option('--cfg', action ='store',help='Openstack settings')
    logFile = None
    file_state = None
    actions = set()
    requires = set()
    options, arguments = p.parse_args()
    # Set up log file
    LoggingLevel = logging.WARNING
    LoggingLevelCounter = 2
    if options.verbose:
        LoggingLevelCounter = LoggingLevelCounter - options.verbose
        if options.verbose == 1:
            LoggingLevel = logging.INFO
        if options.verbose == 2:
            LoggingLevel = logging.DEBUG
    if options.quiet:
        LoggingLevelCounter = LoggingLevelCounter + options.quiet
    if LoggingLevelCounter <= 0:
        LoggingLevel = logging.DEBUG
    if LoggingLevelCounter == 1:
        LoggingLevel = logging.INFO
    if LoggingLevelCounter == 2:
        LoggingLevel = logging.WARNING
    if LoggingLevelCounter == 3:
        LoggingLevel = logging.ERROR
    if LoggingLevelCounter == 4:
        LoggingLevel = logging.FATAL
    if LoggingLevelCounter >= 5:
        LoggingLevel = logging.CRITICAL
    if options.logcfg:
        logFile = options.log_config
    if logFile != None:
        if os.path.isfile(str(options.log_config)):
            logging.config.fileConfig(options.log_config)
        else:
            logging.basicConfig(level=LoggingLevel)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.log_config))
            sys.exit(1)
    else:
        logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")

    if options.state:
        file_state = options.state

    
    process_actions(str(file_state))


    return
if __name__ == "__main__":
    main()
