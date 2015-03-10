import logging
import novaclient.v2.client as nvclient
import json
import uuid
import time
from novaclient.exceptions import OverLimit
import sys

#should delete this
from environ import getenviromentvars

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

class view_buildup(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.instance")
        self.model = model
        self._nova_con = None
    def connect(self):
        if self._nova_con != None:
            return
        self._nova_con = nvclient.Client(**self.model.nova_creds)

    def buildup(self, steering_filename):
        steering_data = read_input(steering_filename)
        output = {}
        images_data = steering_data.get("images", {})
        if len(images_data) == 0:
            return False

        flavor_data = steering_data.get("flavor", {})
        if len(flavor_data) == 0:
            return False

        instance_data = steering_data.get("instances", {})
        if len(instance_data) == 0:
            return False

        label_data = steering_data.get("label", {})

        if not self._nova_con.keypairs.findall(name="mykey"):
            with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
                self._nova_con.keypairs.create(name="mykey", public_key=fpubkey.read())


        imagedict = {}
        for image_uuid in images_data:
            imagename = str(images_data[image_uuid]["OS_IMAGE_NAME"])
            image = self._nova_con.images.find(name=imagename)
            imagedict[image_uuid] = image

        flavordict = {}
        for flavor_uuid in flavor_data:
            flavorname = str(flavor_data[flavor_uuid]["OS_FLAVOR_NAME"])
            flavor = self._nova_con.flavors.find(name=flavorname)
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
                instance = self._nova_con.servers.create(*boot_args, **boot_kwargs)
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
                instance = self._nova_con.servers.get(identified)
                status = instance.status
                if status == 'BUILD':
                    continue
                booted.add(key)
                ourpur[key]['OS_NETWORKS'] = instance.networks
            instance_build.difference_update(booted)
        return ourpur
