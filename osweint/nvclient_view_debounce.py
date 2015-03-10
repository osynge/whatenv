import logging
import json
import uuid
import time
import sys


import subprocess
from command_runner import Command


try:
    import novaclient.v3.client as nvclient
except ImportError:
    try:
        import novaclient.v2.client as nvclient
    except ImportError:
        import novaclient.v1_1.client as nvclient


def read_input(filename):
    f = open(filename)
    json_string = f.read()
    loadedfile = json.loads(json_string)
    return loadedfile


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

def clean_lsblk(intext):
    splittext = intext.split('\n')
    filtered_text = {}
    for line in splittext:
        if len(line) == 0:
            continue
        if line[:4] != "NAME":
            continue
        splitline = line.split('" ')
        if len(splitline) == 0:
            continue
        line_dist = {}
        for item in splitline:
            split_item = item.split('="')
            if len(split_item) != 2:
                continue
            line_dist[split_item[0]] = split_item[1]
        if not 'NAME' in line_dist:
            continue
        filtered_text[line_dist['NAME']] = line_dist
    return filtered_text



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
    disk_details = {}
    for hostname in hostname_short:
        subprocess.call(["ssh-keygen", "-R", hostname])
        croc = Command("ssh -o StrictHostKeyChecking=no root@%s lsblk --pairs --output-all  --bytes" % (hostname))
        rc,stdout,stderr = croc.run(timeout=30)
        if rc != 0:
            continue
        hostname_short_connected.add(hostname)
        disk_details.update(clean_lsblk(stdout))
    hostname_long_connected = set()
    for hostname in hostname_long:
        subprocess.call(["ssh-keygen", "-R", hostname])
        croc = Command("ssh -o StrictHostKeyChecking=no root@%s lsblk --pairs --output-all  --bytes" % (hostname))
        rc,stdout,stderr = croc.run(timeout=30)
        if rc != 0:
            continue
        hostname_long_connected.add(hostname)
        disk_details.update(clean_lsblk(stdout))
    output = dict(instace)
    output['VM_HOSTNAME'] = list(hostname_short.union(hostname_long))
    output['VM_DISK'] = disk_details
    return output


class view_buildup(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.buildup")
        self.model = model
        self._nova_con = None
    def connect(self):
        if self._nova_con != None:
            return
        self._nova_con = nvclient.Client(**self.model.nova_creds)

    def debounce(self, state_filename):

        output_data = read_input(state_filename)
        self.log.debug("here")
        #print output_data
        # Get full list of addresses
        addresses = set()
        for instace in output_data:
            for netwrok in output_data[instace]['OS_NETWORKS']:
                address_list = output_data[instace]['OS_NETWORKS'][netwrok]
                for address in address_list:
                    addresses.add(address)
        pinged = pinghosts(addresses)
        self.log.debug("pinged=%s" % ( pinged))
        # Remove all address from known hosts
        for address in pinged:
            subprocess.call(["ssh-keygen", "-R", address])
        # check all addresses can be connected to.
        connected = sshhosts(pinged)
        self.log.debug("connected=%s" % ( connected))

        for instace in output_data:
            output = update_instance_data(output_data[instace])
            output_data[instace] = output
        #output_data.update(booted)
        f = open(state_filename, 'w')
        json.dump(output_data, f, sort_keys=True, indent=4)
        #print json.dumps(output_data, sort_keys=True, indent=4)
