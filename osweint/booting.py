import os
import time
import novaclient.v1_1.client as nvclient

from novaclient.exceptions import OverLimit
import uuid
import json
import sys
from environ import getenviromentvars
import optparse
import logging
import config
from __version__ import version

def read_input(filename):
    f = open(filename)
    json_string = f.read()
    loadedfile = json.loads(json_string)
    return loadedfile

def bootimages(cfg,input_data):
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
    creds = cfg.get_nova_creds()
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
        try:
            instance = nova.servers.create(*boot_args, **boot_kwargs)
        except OverLimit, E:
            print E
            sys.exit(1)
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
        

def process_actions(cfg,input_name,output_name):
    input_data = read_input(input_name)
    booted = bootimages(cfg, input_data)
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
    p.add_option('--steering', action ='store',help='Steering file to create VM')
    p.add_option('--state', action ='store',help='State file')
    p.add_option('--cfg', action ='store',help='Openstack settings')
    input_file = None
    output_file = None
    file_cfg = None
    actions = set()
    requires = set()
    logFile = None
    cfg = config.cfg()
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
    
    
    if options.cfg:
        cfg.read(options.cfg)
    
    if options.steering:
        input_file = options.steering
        
    if options.state:
        output_file = options.state
    if input_file == None:
        log.error("No input specified")
        sys.exit(1)
    if input_file == None:
        log.error("No output specified")
        sys.exit(1)

    process_actions(cfg,str(input_file),output_file)


    return 
if __name__ == "__main__":
    main() 
