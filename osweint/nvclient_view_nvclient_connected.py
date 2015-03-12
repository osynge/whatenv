import logging
import json
from nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient

import nvclient_view_con
import date_str

class view_nvclient_connected(nvclient_view_con.view_nvclient_con):
    def __init__(self, model):
        nvclient_view_con.view_nvclient_con.__init__(self,model)
        self.log = logging.getLogger("view.nvclient.connected")

    def update_instance(self, ro_server):
        metadata = {}
        for key in ro_server.metadata:
            value = json.loads(ro_server.metadata[key])
            metadata[key] = value
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
        self.log.debug("prcessing:%s" % (ro_server.id))
        self.log.debug("server.status:%s" % (ro_server.status))
        self.log.debug("server.metadata:%s" % (metadata))

        session_id = metadata['WE_SESSION']
        if not session_id in self.model._sessions:
            new_session = model_nvsession()
            new_session.uuid = session_id
            self.model._sessions[session_id] = new_session
        instance_id = metadata['WE_ID']
        if not instance_id in self.model._instances:
            new_instance = model_instance()
            new_instance._md_whenenv['WE_ID'] = instance_id
            self.model._instances[instance_id] = new_instance
        self.model._sessions[session_id].instances.add(str(metadata['WE_ID']))
        try:
            self.model._sessions[session_id].session_created = date_str.datetime_str_decode(metadata['WE_CREATED'])
        except ValueError, E:
            self.log.error(E)
        self.model._instances[instance_id].sessions.add(str(metadata['WE_SESSION']))
        self.model._instances[instance_id].os_id = str(ro_server.id)
        self.model._instances[instance_id]._md_user.update(metadata['WE_USER_LABEL'])

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
        server_list = self._nova_con.servers.list()
        for server in server_list:
            self.update_instance(server)

