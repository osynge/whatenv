
class view_vmclient_config(object):
    def __init__(self, model):
        self.model = model

    def cfg_apply(self,cfg):
        self.model.username = cfg.username
        self.model.password = cfg.password
        self.model.auth_url = cfg.auth_url
        self.model.project_name = cfg.tenant_name
