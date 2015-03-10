import novaclient.v1_1.client as nvclient
from environ import getenviromentvars
import logging
import json
import uuid

from nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient



class view_nvsession(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.nvsession")
        self.model = model

    def env_apply(self):
        env_set_termial = set(["TERMINAL_SSH_CONNECTION",
            "TERMINAL_XAUTHLOCALHOSTNAME",
            "TERMINAL_GPG_TTY"])
        env_set_jenkins = set(["JENKINS_BUILD_TAG",
            "JENKINS_BUILD_URL",
            "JENKINS_EXECUTOR_NUMBER",
            "JENKINS_NODE_NAME",
            "JENKINS_WORKSPACE"])

        env_var = getenviromentvars()
        terminal_use = False
        jenkins_use = False
        terminal_set = env_set_termial.intersection(env_var)
        jenkins_set = env_set_jenkins.intersection(env_var)
        sessionset = set()
        if len(terminal_set) > 0:
            sessionset.add("TERMINAL")
            
        if len(jenkins_set) > 0:
            sessionset.add("JENKINS")
        session_uuid = None
        for session in self.model._sessions:
            if len(self.model._sessions[session].session_type) == 0:
                log.error('TODO:account for this state')
            if self.model._sessions[session].session_type != sessionset:
                continue
            session_terminal_set = env_set_termial.intersection(self.model._sessions[session]._md_whenenv)
            if session_terminal_set != terminal_set:
                continue
            session_jenkins_set = jenkins_set.intersection(self.model._sessions[session]._md_whenenv)
             
            if session_jenkins_set != jenkins_set:
                continue
            thesame = True
            for key in session_terminal_set.union(session_jenkins_set):
                if env_var[key] == self.model._sessions[session]._md_whenenv[key]:
                    continue
                thesame = False
                break
            if not thesame:
                continue
            session_uuid = session
        if session_uuid != None:
             self.model.session_id = session_uuid
             return
        session_uuid = str(uuid.uuid4())
        new_session = model_nvsession()
        new_session.uuid = session_uuid
        new_session.session_type = sessionset
        for key in terminal_set.union(jenkins_set):
            new_session._md_whenenv[key] = env_var[key]
        self.model._sessions[session_uuid] = new_session
        self.model.session_id = session_uuid

class view_delete(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.instance")
        self.model = model
        self._nova_con = None
    def connect(self):
        if self._nova_con != None:
            return
        self._nova_con = nvclient.Client(**self.model.nova_creds)
        
    def instance_by_weid(self, weid):
        server_list = self._nova_con.servers.list()
        for server in server_list:
            #print "prcessing:%s" % (server.id)
            if server.id == self.model._instances[weid].os_id:
                self.log.debug("deleting:%s" % (server.name))
                server.delete()
                self.log.debug("server.status:%s" % (server.status))
        
    def session_by_weid(self, weid):
        for instance in self.model._sessions[weid].instances:
            self.instance_by_weid(instance)
            
    

class view_instance_json(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.instance")
        self.model = model
    def list_images_default(self):
        output = {}
        output["WE_USER_LABEL"] = {}
        for item in self.model._md_user:
            output["WE_USER_LABEL"][item] = self.model._md_user[item]
        for item in self.model._md_whenenv:
            output[item] = self.model._md_whenenv[item]
        if len(self.model.sessions) == 1:
            session_set = self.model.sessions.copy()
            output["WE_SESSION"] = session_set.pop()
        output["OS_ID"] = self.model.os_id        
        output["OS_IMAGE_HUMAN_NAME"] = self.model.os_image_human_name

        output["UUID"] = self.model.uuid
        return output
    
    
class view_session_json(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.instance")
        self.model = model
    def list_images_default(self):
        
        output = {}
        for item in self.model._md_whenenv:
            output[item] = self.model._md_whenenv[item]
        if len(self.model.instances) > 0:
            
            output["INSTANCES"] = list(self.model.instances)
        return output
    
  
    

class view_nvclient_json(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.nvsession")
        self.model = model
    def list_images_default(self):
        output = {}
        for item in self.model._instances:
            obj = view_instance_json(self.model._instances[item])
            output[item] = obj.list_images_default()
        return output
    
    def list_sessions_default(self):
        output = {}
        for item in self.model._sessions:
            obj = view_session_json(self.model._sessions[item])
            as_dict = obj.list_images_default()
            as_dict["CURRENT_SESSION"] = False
            if (self.model.session_id == item):
                as_dict["CURRENT_SESSION"] = True
            output[item] = as_dict
        return output

class view_nvclient_connected(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.nvclient.connected")
        self.model = model
        self._nova_con = None
    def connect(self):
        if self._nova_con != None:
            return
        self._nova_con = nvclient.Client(**self.model.nova_creds)
        
    def update_instance(self, ro_server):
        metadata = {}
        for key in ro_server.metadata:
            value = json.loads(ro_server.metadata[key])
            metadata[key] = value
        required_keys = set(['WE_SESSION',
            'WE_ID',
            'WE_TYPE_UUID',
            'OS_IMAGE_ID',
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
            

class view_vmclient_config(object):
    def __init__(self, model):
        self.model = model
    
    def cfg_apply(self,cfg):
        self.model.nova_creds = cfg.get_nova_creds()
        self.model.keystone_creds = cfg.get_keystone_creds()

    

class controler(object):
    def __init__(self):
        self.model_nvclient = model_nvclient()
        self.connection = None

    def connect(self):
        self.connection = view_nvclient_connected(self.model_nvclient)
        self.connection.connect()
        self.connection.update()
        
    def read_config(self,cfg):
        config = view_vmclient_config(self.model_nvclient)
        config.cfg_apply(cfg)
        #config.env_apply()
        
     
        
    
    def list(self):
        config = view_nvsession(self.model_nvclient)
        config.env_apply()
        outputer = view_nvclient_json(self.model_nvclient)
        print json.dumps(outputer.list_images_default() , sort_keys=True, indent=4)


    def list_sessions(self):
        config = view_nvsession(self.model_nvclient)
        config.env_apply()
        outputer = view_nvclient_json(self.model_nvclient)
        print json.dumps(outputer.list_sessions_default() , sort_keys=True, indent=4)
    
    def delete_session(self):
        config = view_nvsession(self.model_nvclient)
        config.env_apply()
        deleter = view_delete(self.model_nvclient)
        deleter.connect()
        deleter.session_by_weid(self.model_nvclient.session_id)
