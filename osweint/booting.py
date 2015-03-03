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
from __version__ import version

def prototype():
    creds = get_nova_creds()
    nova = nvclient.Client(**creds)
    if not nova.keypairs.findall(name="mykey"):
        with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
            nova.keypairs.create(name="mykey", public_key=fpubkey.read())

    image = nova.images.find(name="SLES12")
    flavor = nova.flavors.find(name="m1.tiny")

    generator = str(uuid.uuid4())

    metadata = {}
    metadata.update(getenviromentvars())


    generator = str(uuid.uuid4())
    metadata['WE_ID'] = generator



    instance_name = "whenenv-%s" % (generator)


    metadata['OS_NAME'] = instance_name

    #print dir(image)

    metadata['OS_IMAGE_ID'] = str(image.id)
    metadata['OS_IMAGE_NAME'] = str(image.name)
    metadata['OS_IMAGE_HUMAN_NAME'] = str(image.human_id)

    instance = nova.servers.create(name=instance_name, image=image, flavor=flavor, key_name="mykey",metadata =  metadata)
    #print metadata
    #instance.metadata.update(metadata)
    #print metadata

    # Poll at 5 second intervals, until the status is no longer 'BUILD'
    status = instance.status
    while status == 'BUILD':
        time.sleep(5)
        # Retrieve the instance again so the status field updates
        instance = nova.servers.get(instance.id)
        status = instance.status
    print "status: %s" % instance.id
    print "status: %s" % status
    metadata['OS_ID'] = unicode(instance.id)


    output_image = {generator : metadata}
    filename = "jenkins-whenenv-booting.json"
    f = open(filename, 'w')
    json.dump(output_image, f, sort_keys=True, indent=4)


def read_input(filename):
    f = open(filename)
    json_string = f.read()
    loadedfile = json.loads(json_string)
    return loadedfile

def bootimages(input_data):
    output = {}
    images_data = input_data.get("images", {})
    if len(images_data) == 0: 
        return False
    
    flavor_data = input_data.get("flavor", {})
    if len(flavor_data) == 0: 
        return False
    
    instance_data = input_data.get("instances", {})
    if len(instance_data) == 0: 
        return False
    
    label_data = input_data.get("label", {})
    
    creds = get_nova_creds()
    nova = nvclient.Client(**creds)
    if not nova.keypairs.findall(name="mykey"):
        with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
            nova.keypairs.create(name="mykey", public_key=fpubkey.read())

    
    imagedict = {}
    for image_uuid in images_data:
        imagename = str(images_data[image_uuid]["OS_IMAGE_NAME"])
        image = nova.images.find(name=imagename)
        imagedict[image_uuid] = image
    
    flavordict = {}
    for flavor_uuid in flavor_data:
        flavorname = str(flavor_data[flavor_uuid]["OS_FLAVOR_NAME"])
        flavor = nova.flavors.find(name=flavorname)
        flavordict[flavor_uuid] = flavor
    
    labeldict = dict(label_data)
     
    
    ourpur = {}
    
    session_id = str(uuid.uuid4())
    
    
    enviroment_metadata = getenviromentvars()
    booting = set()    
    for instance_uuid in instance_data:
        metadata = {}
        label_uuid = []
        image_uuid = instance_data[instance_uuid]["uuid_image"]
        flavor_uuid = instance_data[instance_uuid]["uuid_flavour"]
        if len(labeldict) > 0:
            label_uuid = instance_data[instance_uuid].get("usr_label",[])
        image = imagedict.get(image_uuid,None)
        if image == None:
            continue
        flavor = flavordict.get(flavor_uuid,None)
        if flavor == None:
            continue
        labels = {}
        for lablekey in label_uuid:
            labels.update(labeldict[lablekey])
        generator = str(uuid.uuid4())
        metadata['WE_ID'] = generator
        metadata.update(enviroment_metadata)
        metadata["WE_TYPE_UUID"] = instance_uuid
        
        
        
        instance_name = "whenenv-%s" % (generator)
        metadata['OS_NAME'] = instance_name
        metadata['OS_IMAGE_ID'] = str(image.id)
        metadata['OS_IMAGE_NAME'] = str(image.name)
        metadata['OS_IMAGE_HUMAN_NAME'] = str(image.human_id)
        metadata['WE_SESSION'] = session_id
        metadata['WE_USER_LABEL'] = labels
        foo = {}
        for metakey in metadata:
            foo[metakey] = json.dumps(metadata[metakey])

        #instance = nova.servers.create(instance_name, image, flavor, key_name="mykey",metadata =  foo)
        boot_args = [instance_name, image, flavor] 

        boot_kwargs = {'files': {}, 'userdata': None, 'availability_zone': None, 'nics': [], 'block_device_mapping': {}, 'max_count': 1, 'meta': foo, 'key_name': 'mykey', 'min_count': 1, 'scheduler_hints': {}, 'reservation_id': None, 'security_groups': [], 'config_drive': None}

        instance = nova.servers.create(*boot_args, **boot_kwargs)
        
        metadata['OS_ID'] = unicode(instance.id)
        ourpur[generator] = metadata
        booting.add(generator)
    
    instance_build = set(booting)
    while len(instance_build) > 0:
        time.sleep(5)
        booted = set()
        for key in booting:
            identified = ourpur[key]['OS_ID']
            instance = nova.servers.get(identified)
            status = instance.status
            if status == 'BUILD':
                continue
            booted.add(key)
            ourpur[key]['OS_NETWORKS'] = instance.networks
        instance_build.difference_update(booted)
    return ourpur
        

def process_actions(input_name,output_name):
    input_data = read_input(input_name)
    booted = bootimages(input_data)
    #print json.dumps(booted, sort_keys=True, indent=4)
    try:
        output_data = read_input(output_name)
    except:
        output_data = {}
    output_data.update(booted)
    f = open(output_name, 'w')
    json.dump(output_data, f, sort_keys=True, indent=4)
    
def main():
    
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logcfg', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-v', '--verbose', action ='count',help='Change global log level, increasing log output.', metavar='LOGFILE')
    p.add_option('-q', '--quiet', action ='count',help='Change global log level, decreasing log output.', metavar='LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Configuration file.', metavar='CFG_FILE')
    p.add_option('--input', action ='store',help='Called by udev $name')
    p.add_option('--output', action ='store',help='List all known instalations')
    p.add_option('--prototype', action ='store_true',help='List all known instalations')

    input_file = None
    output_file = None
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
        output['pmpman.path.cfg'] = options.logcfg

    log = logging.getLogger("main")
    if options.prototype:
        prototype()
        sys.exit (0)
    if options.input:
        input_file = options.input
        
    if options.output:
        output_file = options.output

    if options.database:
        output['pmpman.rdms'] = options.database
    process_actions(str(input_file),output_file)


    return 
if __name__ == "__main__":
    main() 
