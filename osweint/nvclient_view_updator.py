import logging
import json
import date_str
import uuid

from novaclient.exceptions import OverLimit,from_response, NotFound

from nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient, model_flavor,model_images, model_instance_network

LOG = logging.getLogger(__name__)


class view_mdl_update_nvclient(object):
    def __init__(self, model, con):
        self.model = model
        self.nova_con = con

    def update_flavor(self, ro_server):
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
        #LOG.error("update_flavor")
        #LOG.error(dir(ro_server))
        #LOG.error(ro_server.id)

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
        network_list = self.nova_con.networks.list()
        for network in network_list:
            LOG.error("network:%s=%s" % ( network.human_id,network.id))
        new_networks = set()
        found_networks = set()
        known = set(self.model._networks.keys())
        network_list = self.nova_con.networks.list()
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

    def update_instance_network(self, instance_id):
        try:
            instance = self.nova_con.servers.get(self.model._instances[instance_id].os_id)
        except NotFound:
            return

        os_dict = {}
        known_networks = set()
        for network in instance.networks:
            os_dict[str(network)] = instance.networks[network]
        # Delete extra networks
        for netobjkey in self.model._instances[instance_id].networks.keys():
            known_networks.add(self.model._instances[instance_id].networks[netobjkey].os_name)
        set_os_netwoks_found = set(os_dict.keys())
        missing = set_os_netwoks_found.difference(known_networks)
        extra = known_networks.difference(set_os_netwoks_found)
        intersection = known_networks.intersection(set_os_netwoks_found)
        # delete extra
        for addressid in self.model._instances[instance_id].networks.keys():
            if not self.model._instances[instance_id].networks[addressid].os_name in intersection:
                del self.model._instances[instance_id].networks[addressid]
        # add missing
        for network in missing:
            for address in os_dict[network]:
                networkid = str(uuid.uuid1())
                netobj = model_instance_network()
                netobj.os_name = network
                netobj.os_address = address
                self.model._instances[instance_id].networks[networkid] = netobj
        for network in intersection:
            known_addresses = set()
            for netobjkey in self.model._instances[instance_id].networks.keys():
                if self.model._instances[instance_id].networks[netobjkey].os_name != network:
                    continue
                known_addresses.add(self.model._instances[instance_id].networks[netobjkey].os_address)
            missing_addresses = known_addresses.difference(os_dict[network])
            extra_addresses = set(os_dict[network]).difference(known_addresses)
            for netobjkey in self.model._instances[instance_id].networks.keys():
                if self.model._instances[instance_id].networks[netobjkey].os_name != network:
                    continue
                if not self.model._instances[instance_id].networks[netobjkey].os_address in extra_addresses:
                    continue
                del self.model._instances[instance_id].networks[netobjkey]
            for address in missing_addresses:
                networkid = str(uuid.uuid1())
                netobj = model_instance_network()
                netobj.os_name = network
                netobj.os_address = address
                self.model._instances[instance_id].networks[networkid] = netobj

    def update_instance(self, ro_server):
        metadata = {}
        #LOG.debug("prcessing:%s" % (dir(ro_server)))
        #LOG.debug("accessIPv4:%s" % (ro_server.accessIPv4))
        #LOG.debug("is_loaded:%s" % (ro_server.is_loaded()))

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
        #LOG.debug("prcessing:%s" % (ro_server.id))
        #LOG.debug("server.status:%s" % (ro_server.status))
        #LOG.debug("server.metadata:%s" % (metadata))

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
            LOG.error(E)
        self.model._instances[instance_id].sessions.add(str(metadata['WE_SESSION']))

        if 'WE_USER_LABEL' in metadata:
            LOG.error("WE_USER_LABEL='%s'" % (metadata['WE_USER_LABEL']))
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

    def get_instances_booting(self):
        instance_id_booting = set()
        for instance_id in self.model._instances:
            if self.model._instances[instance_id].status == 'BUILD':
                instance_id_booting.add(instance_id)
        return instance_id_booting

    def update_instances_all(self):
        server_list = self.nova_con.servers.list()
        for server in server_list:
            self.update_instance(server)
        # get status for instances after booted.
        instance_id_booting = self.get_instances_booting()
        while len(instance_id_booting) > 0:
            time.sleep(5)
            for booting_instance in instance_id_booting:
                instance = self.nova_con.servers.get(self.model._instances[instance_id].os_id)
                self.update_instance(instance)
            instance_id_booting = self.get_instances_booting()
        for instance_id in self.model._instances.keys():
            self.update_instance_network(instance_id)





    def update(self):

        flavor_list = self.nova_con.flavors.list()
        for flavor in flavor_list:
            self.update_flavor(flavor)
        images_list = self.nova_con.images.list()
        for images in images_list:
            self.update_images(images)
        self.update_network()
        self.update_instances_all()

