import logging
import json
import uuid
import time
from novaclient.exceptions import OverLimit
import sys
import os.path
import nvclient_view_con
import date_str

#should delete this
from environ import getenviromentvars
from osweint.nvclient_view_nvclient_connected import view_nvclient_connected as view_nvclient_connected
class Error(Exception):
    """
    Error
    """

    def __str__(self):
        doc = self.__doc__.strip()
        return ': '.join([doc] + [str(a) for a in self.args])

def read_input(filename):
    f = open(filename)
    json_string = f.read()
    loadedfile = json.loads(json_string)
    return loadedfile

class view_buildup(nvclient_view_con.view_nvclient_con):
    def __init__(self, model):
        nvclient_view_con.view_nvclient_con.__init__(self,model)
        self.log = logging.getLogger("view.buildup")

    def enstantiate(self, steering_filename,builder):
        if not os.path.isfile(steering_filename):
            raise Error("Steering file '%s' does not exist" % steering_filename)
        try:
            steering_data = read_input(steering_filename)
        except ValueError, e:
            self.log.error("Failed to load steering file")
            self.log.error(e)
            raise Error("Steering file '%s' loading error:%s" % (steering_filename,e))
        output = {}
        image_data = steering_data.get("images", {})
        if len(image_data) == 0:
            return False

        flavor_data = steering_data.get("flavor", {})
        if len(flavor_data) == 0:
            return False

        instance_data = steering_data.get("instances", {})
        if len(instance_data) == 0:
            return False

        network_data = steering_data.get("network", {})
        self.log.error("network_data=%s" % (network_data))
        if len(network_data) == 0:
            return False

        label_data = steering_data.get("label", {})

        # we have intial data


        session_id = builder.get_session_current()
        if session_id == None:
            session_id = builder.create_session(str(uuid.uuid4()))
            builder.update()
        if session_id == None:
            self.log.error("session_id=%s" % (session_id))
            return False
        self.log.error("session_id=%s" % (session_id))
        known_images = set(self.model._images.keys())
        known_flavors = set(self.model._flavors.keys())
        known_networks = set(self.model._networks.keys())

        imagedict = {}
        for image_uuid in image_data:
            imagename = str(image_data[image_uuid]["OS_IMAGE_NAME"])
            matching_names = set()
            for image_id in known_images:
                if self.model._images[image_id].os_name == imagename:
                    matching_names.add(image_id)
            imagedict[image_uuid] = matching_names

        flavordict = {}
        for flavor_uuid in flavor_data:
            flavorname = str(flavor_data[flavor_uuid]["OS_FLAVOR_NAME"])
            matching_flavor = set()
            for flavor_id in known_flavors:
                if self.model._flavors[flavor_id].os_name == flavorname:
                    matching_flavor.add(flavor_id)
            flavordict[flavor_uuid] = matching_flavor
        self.log.error("flavordict=%s" % (flavordict))
        networkdict = {}
        for network_uuid in network_data:
            networkname = str(network_data[network_uuid]["OS_NETWORK_NAME"])
            matching_network = set()
            for network_id in known_networks:
                if self.model._networks[network_id].os_name == networkname:
                    matching_network.add(network_id)
            networkdict[network_uuid] = matching_network
        self.log.error("networkdict=%s" % (networkdict))
        labeldict = dict(label_data)


        ourpur = {}

        session_created = date_str.datetime_encoded_str()

        enviroment_metadata = getenviromentvars()
        booting = set()
        for instance_uuid in instance_data:
            instance_id = builder.create_instance(str(uuid.uuid4()),session_id)
            if instance_id == None:
                self.log.error("failed to create instance=%s" % (instance_uuid))
                continue



            metadata = {}
            label_uuid = []
            image_uuid = instance_data[instance_uuid]["uuid_image"]
            flavor_uuid = instance_data[instance_uuid]["uuid_flavour"]
            network_uuid = instance_data[instance_uuid]["uuid_network"]

            if len(labeldict) > 0:
                label_uuid = instance_data[instance_uuid].get("usr_label",[])
            image = set(imagedict.get(image_uuid,set()))
            if len(image) != 1:
                self.log.error("not found image_uuid=%s" % (image))
                continue
            flavor = set(flavordict.get(flavor_uuid,set()))
            if len(flavor) != 1:
                self.log.error("not found flavor_uuid=%s" % (flavor))
                continue
            network = set(networkdict.get(network_uuid,set()))
            if len(network) != 1:
                self.log.error("not found network_uuid=%s" % (network_uuid))
                self.log.error("known=%s" % (networkdict))
                self.log.error("network=%s" % (network))
                continue
            self.log.error("image=%s" % (image))


            image_id = image.pop()
            flavor_id = flavor.pop()
            network_id = network.pop()
            self.model._instances[instance_id].flavors = flavor
            self.log.debug("network_uuid=%s" % (network_uuid))
            self.log.debug("network_id=%s" % (network_id))
            self.log.debug("flavor=%s" % (flavor))

            instance_data[instance_uuid]
            labels = {}
            image_labales = image_data[image_uuid].get("usr_label",[])
            for lablekey in image_labales:
                labels.update(labeldict[lablekey])
            flavor_labales = flavor_data[flavor_uuid].get("usr_label",[])
            for lablekey in flavor_labales:
                labels.update(labeldict[lablekey])
            for lablekey in label_uuid:
                labels.update(labeldict[lablekey])

            generator = str(uuid.uuid4())
            metadata['WE_ID'] = generator
            metadata.update(enviroment_metadata)
            metadata["WE_TYPE_UUID"] = instance_uuid
            metadata["WE_CREATED"] = session_created


            self.log.debug("image_id=%s" % (image_id))
            instance_name = "whatenv-%s" % (generator)
            metadata['WE_SESSION'] = session_id
            metadata['WE_USER_LABEL'] = labels
            metadata['OS_IMAGE_NAME'] = self.model._images[image_id].os_name
            metadata['OS_NAME'] = instance_name
            metadata['OS_IMAGE_HUMAN_NAME'] = instance_name
            metadata['OS_FLAVOR_ID'] = self.model._flavors[flavor_id].os_id
            metadata['OS_NETWORK_NAME'] = self.model._networks[network_id].os_name
            metadata['OS_NETWORK_ID'] = self.model._networks[network_id].os_id
            builder.add_metadata(instance_id,metadata)
            builder.boot_instance(instance_id,image_id,flavor_id,self.model._networks[network_id].os_id)



    def buildup(self, steering_filename):
        if not os.path.isfile(steering_filename):
            raise Error("Steering file '%s' does not exist" % steering_filename)
        try:
            steering_data = read_input(steering_filename)
        except ValueError, e:
            self.log.error("Failed to load steering file")
            self.log.error(e)
            sys.exit(1)
        output = {}
        image_data = steering_data.get("images", {})
        if len(image_data) == 0:
            return False

        flavor_data = steering_data.get("flavor", {})
        if len(flavor_data) == 0:
            return False

        instance_data = steering_data.get("instances", {})
        if len(instance_data) == 0:
            return False

        label_data = steering_data.get("label", {})

        if not self._nova_con.keypairs.findall(name="mykey"):
            if not os.path.isfile('~/.ssh/id_rsa.pub'):
                self.log.error("Public key file: '~/.ssh/id_rsa.pub' is missing")
                sys.exit(1)
            with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
                self._nova_con.keypairs.create(name="mykey", public_key=fpubkey.read())


        imagedict = {}
        for image_uuid in image_data:
            imagename = str(image_data[image_uuid]["OS_IMAGE_NAME"])
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
        session_created = date_str.datetime_encoded_str()

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
            image_labales = image_data[image_uuid].get("usr_label",[])
            for lablekey in image_labales:
                labels.update(labeldict[lablekey])
            flavor_labales = flavor_data[flavor_uuid].get("usr_label",[])
            for lablekey in flavor_labales:
                labels.update(labeldict[lablekey])
            for lablekey in label_uuid:
                labels.update(labeldict[lablekey])

            generator = str(uuid.uuid4())
            metadata['WE_ID'] = generator
            metadata.update(enviroment_metadata)
            metadata["WE_TYPE_UUID"] = instance_uuid
            metadata["WE_CREATED"] = session_created


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

            boot_kwargs = {'files': {},
                'userdata': None,
                'availability_zone': None,
                'nics': [],
                'block_device_mapping': {},
                'max_count': 1,
                'meta': foo,
                'key_name':
                'mykey',
                'min_count': 1,
                'scheduler_hints': {},
                'reservation_id': None,
                'security_groups': [],
                'config_drive': None
            }
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
