import logging

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

