import logging

api_version = None

try:
    import novaclient.v2.client as nvclient
    api_version = 2
except ImportError:
    import novaclient.v1_1.client as nvclient
    api_version = 1


class view_nvclient_con(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.nvclient.connected")
        self.model = model
        self._nova_con = None
    def connect_v3(self):
        d = {}
        d['auth_url'] = self.model.auth_url
        self._nova_con = nvclient.Client(self.model.username,
            self.model.password,
            self.model.project_name,
            **d
            )
    def connect_v2(self):
        d = {}
        d['username'] = self.model.username
        d['api_key'] = self.model.password
        d['auth_url'] = self.model.auth_url
        d['project_id'] = self.model.project_name
        self._nova_con = nvclient.Client(**d)
    def connect_v1(self):
        d = {}
        d['username'] = self.model.username
        d['api_key'] = self.model.password
        d['auth_url'] = self.model.auth_url
        d['project_id'] = self.model.project_name
        self._nova_con = nvclient.Client(**d)

    def connect(self):
        if self._nova_con != None:
            return
        if api_version == 3:
            return self.connect_v3()
        if api_version == 1:
            return self.connect_v1()
        if api_version == 2:
            return self.connect_v2()

