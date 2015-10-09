import logging
import json
from nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient, model_flavor,model_images

import nvclient_view_con
import date_str
import nvclient_view_nvsession
import uuid

from environ import getenviromentvars
from novaclient.exceptions import OverLimit,from_response
import date_str
import time

class view_nvclient_connected(nvclient_view_con.view_nvclient_con):
    def __init__(self, model):
        nvclient_view_con.view_nvclient_con.__init__(self,model)
        self.log = logging.getLogger("view.nvclient.connected")


    def update_flavor(self, ro_server):
        #self.log.error("update_flavor")
        #self.log.error(dir(ro_server))
        #self.log.error(ro_server.id)

        known = set(self.model._flavors.keys())
        candidates = set()
        for item in known:
            if self.model._flavors[item].os_id != ro_server.id:
                continue
            candidates.add(item)
        if len(candidates) == 0:
            new_flavor_uuid = str(uuid.uuid4())
            new_flavor = model_flavor()
            new_flavor.uuid = new_flavor_uuid
            new_flavor.os_id = ro_server.id
            new_flavor.os_name = ro_server.name
            self.model._flavors[new_flavor_uuid] = new_flavor
            candidates.add(new_flavor_uuid)
        candidate_names_flavor_name = set()



    def update_images(self, ro_server):
        #self.log.error("update_flavor")
        #self.log.error(dir(ro_server))
        #self.log.error(ro_server.id)

        known = set(self.model._images.keys())
        candidates = set()
        for item in known:
            if self.model._images[item].os_id != ro_server.id:
                continue
            candidates.add(item)
        if len(candidates) == 0:
            new_flavor_uuid = str(uuid.uuid4())
            new_flavor = model_images()
            new_flavor.uuid = new_flavor_uuid
            new_flavor.os_id = ro_server.id
            new_flavor.os_name = ro_server.name
            self.model._images[new_flavor_uuid] = new_flavor
            candidates.add(new_flavor_uuid)
        candidate_names_flavor_name = set()

        for item in candidates:
            if self.model._images[item].os_name != ro_server.name:
                continue
            self.model._images[item].os_name = ro_server.name


    def update_network(self):
        print self.model._networks
        network_list = self._nova_con.networks.list()
        for network in network_list:
            self.log.error("network:%s=%s" % ( network.human_id,network.id))
        new_networks = set()
        found_networks = set()
        known = set(self.model._networks.keys())
        network_list = self._nova_con.networks.list()
        for network in network_list:
            os_human_name = str(network.human_id)
            os_id = str(network.id)
            referance = None
            for item in known:
                if self.model._networks[item].os_name == os_human_name:
                    referance = item
                    break
            if referance != None:
                self.model._networks[referance].os_id = os_id
            else:
                identifier = str(uuid.uuid4())
                new_network = model_nvnetwork()
                new_network.os_id = os_id
                new_network.os_name = os_human_name
                self.model._networks[identifier] = new_network

    def update_instance(self, ro_server):
        metadata = {}
        #self.log.debug("prcessing:%s" % (dir(ro_server)))
        #self.log.debug("accessIPv4:%s" % (ro_server.accessIPv4))
        #self.log.debug("is_loaded:%s" % (ro_server.is_loaded()))

        for key in ro_server.metadata:
            value = json.loads(ro_server.metadata[key])
            metadata[key] = str(value)
        required_keys = set(['WE_SESSION',
            'WE_ID',
            'WE_TYPE_UUID',
            'OS_IMAGE_ID',
            'WE_CREATED',
            ])
        missing_keys = required_keys.difference(metadata)
        if len(missing_keys) > 0:
            return
        defaultable_keys = set(['WE_USER_LABEL'])
        default_keys = defaultable_keys.difference(metadata)
        for key in default_keys:
            metadata[key] = {}
        #self.log.debug("prcessing:%s" % (ro_server.id))
        #self.log.debug("server.status:%s" % (ro_server.status))
        #self.log.debug("server.metadata:%s" % (metadata))

        session_id = metadata['WE_SESSION']
        if not session_id in self.model._sessions:
            new_session = model_nvsession()
            new_session.uuid = session_id
            self.model._sessions[session_id] = new_session
        instance_id = metadata['WE_ID']
        if not instance_id in self.model._instances:
            new_instance = model_instance()
            new_instance._md_whenenv['WE_ID'] = instance_id
            new_instance.sessions.add(session_id)
            self.model._instances[instance_id] = new_instance
        # Now we know we have instances and sessiosn objects.

        self.model._instances[instance_id].status = str(ro_server.status)
        self.model._instances[instance_id].os_id = str(ro_server.id)

        # now process the metadata we retrived.
        self.model._sessions[session_id].instances.add(str(metadata['WE_ID']))
        try:
            self.model._sessions[session_id].session_created = date_str.datetime_str_decode(metadata['WE_CREATED'])
        except ValueError, E:
            self.log.error(E)
        self.model._instances[instance_id].sessions.add(str(metadata['WE_SESSION']))

        if 'WE_USER_LABEL' in metadata:
            self.log.error("WE_USER_LABEL='%s'" % (metadata['WE_USER_LABEL']))
            if isinstance(metadata['WE_USER_LABEL'], basestring):
                try:
                    asobj = json.loads(metadata['WE_USER_LABEL'])
                except (ValueError,TypeError) as e:
                    cleaned = metadata['WE_USER_LABEL'].replace("u'", ' "').replace("']", '" ] ').replace("':", '" :').replace("'}", '" }').replace("',", '" ,')
                    asobj = json.loads(cleaned)
                self.model._instances[instance_id]._md_user.update(asobj)
                metadata['WE_USER_LABEL'] = asobj

        env_set_termial = set(["TERMINAL_SSH_CONNECTION",
            "TERMINAL_XAUTHLOCALHOSTNAME",
            "TERMINAL_GPG_TTY"])
        env_set_jenkins = set(["JENKINS_BUILD_TAG",
            "JENKINS_BUILD_URL",
            "JENKINS_EXECUTOR_NUMBER",
            "JENKINS_NODE_NAME",
            "JENKINS_WORKSPACE"])
        terminal_set = env_set_termial.intersection(metadata)
        jenkins_set = env_set_jenkins.intersection(metadata)
        sessionset = set()
        updateset = set()
        if len(terminal_set) > 0:
            sessionset.add("TERMINAL")
            updateset = updateset.union(terminal_set)
        if len(jenkins_set) > 0:
            sessionset.add("JENKINS")
            updateset = updateset.union(jenkins_set)
        self.model._sessions[session_id].session_type = sessionset

        for key in updateset:
            self.model._sessions[session_id]._md_whenenv[key] = metadata[key]


    def update(self):
        flavor_list = self._nova_con.flavors.list()
        for flavor in flavor_list:
            self.update_flavor(flavor)
        images_list = self._nova_con.images.list()
        for images in images_list:
            self.update_images(images)
        self.update_network()
        server_list = self._nova_con.servers.list()
        for server in server_list:
            self.update_instance(server)



    def list_sessions_ids(self):
        #self.log.debug("starting list_sessions_ids")

        return set(self.model._sessions)

    def get_session_current(self):
        #self.log.error("get_session_current")
        if self.model.session_id == None:
            config = nvclient_view_nvsession.view_nvsession(self.model)
            match_sessions = config.get_mattching_sessions()
            #self.log.error("match_sessions:%s" % (match_sessions))
            if len(match_sessions) == 1:
                self.model.session_id = match_sessions.pop()
            #self.log.error("match_sessions:id:%s" % (self.model.session_id))
        #self.log.error("get_session_current:id:%s" % (self.model.session_id))
        if self.model.session_id == None:
            return None
        return str(self.model.session_id)

    def list_instance_id(self,session_name):
        output = set()
        if not session_name in self.model._sessions.keys():
            return output
        return set(self.model._sessions[session_name].instances)

    def delete_instance_id(self, weid_list):
        os_id_list = set()
        we_id_mapping = {}
        for weid in weid_list:
            if not weid in self.model._instances.keys():
                self.log.error("did not find sessionid:%s" % (weid))
                continue
            we_id_mapping[weid] = self.model._instances[weid].os_id
            os_id_list.add(self.model._instances[weid].os_id)
        server_list = self._nova_con.servers.list()
        for server in server_list:
            if server.id in os_id_list:
                self.log.debug("deleting:%s" % (server.name))
                try:
                    server.delete()
                except:
                    pass

        for weid in we_id_mapping.keys():
            #self.log.debug("weid:%s" % (weid))
            #self.log.debug("server.status:%s" % (server.status))
            for session in self.model._instances[weid].sessions:
                #self.log.debug("self.model._instances[weid].sessions:%s" % (session))
                #self.log.debug("instances:%s" % (self.model._sessions[session].instances))

                self.model._sessions[session].instances.remove(weid)
                #self.log.debug("instances:%s" % (self.model._sessions[session].instances))

            del(self.model._instances[weid])


    def create_session(self,session_id):
        self._nova_con.images.list()

        if not self._nova_con.keypairs.findall(name="mykey"):
            if not os.path.isfile('~/.ssh/id_rsa.pub'):
                self.log.error("Public key file: '~/.ssh/id_rsa.pub' is missing")
                sys.exit(1)
            with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
                self._nova_con.keypairs.create(name="mykey", public_key=fpubkey.read())


        #imagedict = {}
        #for image_uuid in image_data:
        #    imagename = str(image_data[image_uuid]["OS_IMAGE_NAME"])
        #    image = self._nova_con.images.find(name=imagename)
        #    imagedict[image_uuid] = image

        flavordict = {}
        #for flavor_uuid in flavor_data:
        #    flavorname = str(flavor_data[flavor_uuid]["OS_FLAVOR_NAME"])
        #    flavor = self._nova_con.flavors.find(name=flavorname)
        #    flavordict[flavor_uuid] = flavor

        env_var = getenviromentvars()
        env_set_termial = set(["TERMINAL_SSH_CONNECTION",
            "TERMINAL_XAUTHLOCALHOSTNAME",
            "TERMINAL_GPG_TTY"])
        env_set_jenkins = set(["JENKINS_EXECUTOR_NUMBER",
            "JENKINS_NODE_NAME"])
        env_set_shared = set(["WE_HOSTNAME",
            "TERMINAL_USERNAME"])
        shared_set = env_set_shared.intersection(env_var)
        terminal_set = env_set_termial.intersection(env_var)
        jenkins_set = env_set_jenkins.intersection(env_var)
        sessionset = set()
        if len(terminal_set) > 0:
            sessionset.add("TERMINAL")

        if len(jenkins_set) > 0:
            sessionset.add("JENKINS")


        ourpur = {}
        session_created = date_str.datetime_encoded_str()



        new_session = model_nvsession()
        new_session.uuid = session_id
        new_session._md_whenenv = getenviromentvars()
        new_session.session_created = session_created
        new_session.session_type = sessionset
        self.model._sessions[session_id] = new_session
        processing_env_set = shared_set.union(terminal_set.union(jenkins_set))
        for key in processing_env_set:
            new_session._md_whenenv[key] = env_var[key]
        return session_id

    def create_instance(self,instance_id,session_id):
        if not session_id in self.model._sessions.keys():
            self.log.error("No session found")
            return None
        if not instance_id in self.model._instances:
            new_instance = model_instance()
            new_instance._md_whenenv['WE_ID'] = instance_id
            new_instance.sessions = set([session_id])
            self.model._instances[instance_id] = new_instance


        self.model._sessions[session_id].instances.add(str(instance_id))
        return instance_id

    def gen_metadata(self,instance_id):
        session_id = iter(self.model._instances[instance_id].sessions).next()

        metadata = {}
        if not instance_id in self.model._instances.keys():
            return metadata


        for key in self.model._instances[instance_id]._md_whenenv.keys():
            metadata[key] = self.model._instances[instance_id]._md_whenenv[key]

        for key in self.model._sessions[session_id]._md_whenenv.keys():
            metadata[key] = self.model._sessions[session_id]._md_whenenv[key]

        metadata['OS_IMAGE_ID'] = self.model._instances[instance_id].os_imageid
        if self.model._instances[instance_id].os_id != None:
            metadata['OS_ID'] = self.model._instances[instance_id].os_id
        if self.model._instances[instance_id].os_name != None:
            metadata['OS_NAME'] = self.model._instances[instance_id].os_name
        if self.model._instances[instance_id].os_image_human_name != None:
            metadata['OS_IMAGE_HUMAN_NAME'] = self.model._instances[instance_id].os_image_human_name
        if self.model._instances[instance_id].os_id != None:
            metadata['OS_IMAGE_ID'] = self.model._instances[instance_id].os_id
        if self.model._instances[instance_id].os_id != None:
            metadata['WE_TYPE_UUID'] = self.model._instances[instance_id].os_id



        metadata['WE_SESSION'] = session_id

        foo = {}
        for metakey in metadata:
            foo[metakey] = json.dumps(metadata[metakey])

        return metadata


    def add_metadata(self,instance_id,metadata):
        if not instance_id in self.model._instances.keys():
            self.log.error("Invalid instance_id=%s" % (instance_id))
            return False
        inmetadata = set(metadata.keys())
        session_id = iter(self.model._instances[instance_id].sessions).next()
        current_session = set(self.model._sessions[session_id]._md_whenenv.keys())
        current_instance = set(self.model._instances[instance_id]._md_whenenv.keys())
        current_keys = current_session.union(current_instance)
        newkeys = inmetadata.difference(current_keys)
        for key in newkeys:
            self.model._instances[instance_id]._md_whenenv[key] = metadata[key]


    def boot_instance(self,instance_id,images_id,flavor_id,network_id):





        metadata = self.gen_metadata(instance_id)

        needed_keys =  ['WE_ID',
            "WE_TYPE_UUID",
            "WE_CREATED",
            'OS_NAME',
            'OS_IMAGE_ID',
            'OS_IMAGE_NAME',
            'OS_IMAGE_HUMAN_NAME',
            'WE_SESSION',
            'OS_FLAVOR_ID',

            ]
        required_keys = set(needed_keys)
        metadata_keys = set(metadata.keys())


        missing_required = required_keys.difference(metadata_keys)
        # now default soem values
        if "WE_CREATED" in missing_required:
            metadata["WE_CREATED"] = date_str.datetime_encoded_str()

        metadata_keys = set(metadata.keys())
        missing_required = required_keys.difference(metadata_keys)
        if len(missing_required) > 0:
            self.log.error("Cannnot launch %s: missing %s" % (instance_id, ",".join(missing_required)))
            return

        #self.log.error("rdiff=%s" %(required_keys.difference(metadata_keys)))
        #self.log.error("diff=%s" %(metadata_keys.difference(required_keys)))

        foo = {}
        for metakey in metadata:
            foo[metakey] = json.dumps(metadata[metakey])

        instance_name = "whenenv-%s" % (instance_id)
        #instance = nova.servers.create(instance_name, image, flavor, key_name="mykey",metadata =  foo)
        os_image_id = metadata["OS_IMAGE_ID"]
        os_flavor_id = metadata["OS_FLAVOR_ID"]

        boot_args = [instance_name, self.model._images[images_id].os_id, self.model._flavors[flavor_id].os_id]
        network_list = self._nova_con.networks.list()
        for network in network_list:
            self.log.error("network:%s=%s" % ( network.human_id,network.id))
                
        boot_kwargs = {'files': {},
            'userdata': None,
            'availability_zone': None,
            'nics': [{ 'net-id': network_id}],
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
            self.log.error("overlimit:" %(E))
            return None
        self.model._instances[instance_id].os_id = unicode(instance.id)
        boot_delay = True
        while boot_delay:
            time.sleep(5)
            booted = set()
            try:
                instance = self._nova_con.servers.get(self.model._instances[instance_id].os_id)
            except:
                continue
            status = instance.status
            if status == 'BUILD':
                continue
            boot_delay = False
        return instance_id

    def list_flavor_id(self):
        return set(self.model._flavors.keys())

    def list_flavor_os_id(self,skey):
        return set(self.model._flavors[skey].os_id)

    def list_images_id(self):
        return set(self.model._images.keys())

