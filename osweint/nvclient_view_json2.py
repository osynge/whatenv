import logging
import json

class view_json_instance_network(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.instance")
        self.model = model
    def list_images_default(self):
        output = {}
        output["OS_NAME"] = self.model.os_name
        output["OS_ADDRESS"] = self.model.os_address
        output["WE_PING"] = self.model.pinged
        output["WE_SSH"] = self.model.sshed
        return output


class view_json_instance(object):
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
        networks = {}
        for net in self.model.networks.keys():
            netobj = view_json_instance_network(self.model.networks[net])
            networks[net] = netobj.list_images_default()


        output["OS_NETWORKS"] = networks
        return output
    def load_images_default(self,decoded_obj):
        for item in decoded_obj:

            if item == "WE_USER_LABEL":
                self.model._md_user = decoded_obj[item]
                continue
            if item == "OS_ID":
                self.model.os_id = decoded_obj[item]
                continue
            if item == "OS_IMAGE_HUMAN_NAME":
                self.model.os_image_human_name = decoded_obj[item]
                continue
            if item == "WE_SESSION":
                continue
            self.model._md_whenenv[item] = decoded_obj[item]


class view_json_client(object):
    def __init__(self, model):
        self.log = logging.getLogger("view_json")
        self.model = model
    def dump_session(self,session_id):
        output = {}
        if session_id in self.model._sessions.keys():
            session = {}
            instances = set(self.model._sessions[session_id].instances)
            for instance_id in instances:
                instance_obj = view_json_instance(self.model._instances[instance_id])
                session[instance_id] = instance_obj.list_images_default()
            output[session_id] = session
        return output

    def load_session(self, decoded_obj, session_id):
        for session_id in decoded_obj:
            pass

    def persist(self,filename):
        dictmdl = self.dump_session(self.model.session_id)
        fp = open(filename,'w')
        json.dump(dictmdl, fp, sort_keys=True, indent=4)
        fp.close()

    def load(self,filename):
        fp = open(filename,'r')
        json.load(fp)
        self.load_session(dictmdl, self.model.session_id)
        fp.close()
