import logging
import date_str
from nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient

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
        if self.model.session_created != None:
            output["CREATED"] = date_str.datetime_encoded_str(self.model.session_created)
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

    def load_sessions_default(self,decoded_obj):
        for key in decoded_obj:
            if not key in self.model._instances.keys():
                new_instance = model_instance()
                self.model._instances[key] = model_instance()
            instance_view = view_instance_json(self.model._instances[key])
            instance_view.load_images_default(decoded_obj[key])
            
