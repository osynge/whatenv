


class model_nvsession(object):
    def __init__(self):
        self.uuid = None
        self.session_type = set()
        self.session_active = False
        self.session_created = None
        self.instances = set()
        self._md_whenenv = {}


class model_nvnetwork(object):
    def __init__(self):
        self.os_id = None
        self.os_name = None
        self.ipv4 = None
    def __repr__(self):
        return "<mnet %s,%s>" % (self.os_id, self.os_name)

class model_flavor(object):
    def __init__(self):
        self.uuid = None
        self.os_name = None
        self.os_id = None


class model_flavor(object):
    def __init__(self):
        self.uuid = None
        self.os_name = None
        self.os_id = None

class model_images(object):
    def __init__(self):
        self.uuid = None
        self.os_name = None
        self.os_id = None

class model_instance_network(object):
    def __init__(self):
        self.os_name = None
        self.os_address = None
        self.pinged = False
        self.sshed = False
    def __repr__(self):
        return "<min %s,%s>" % (self.os_name, self.os_address)

class model_instance(object):
    def __init__(self):
        self._md_whenenv = {}
        self._md_user = {}
        self.os_id = None
        self.os_imageid = None
        self.os_name = None
        self.os_image_human_name = None
        self.sessions = set()
        self.flavors = set()
        self.images = set()
        # Values taken from nova api
        # in addition a "REQUESTED" state.
        self.status = None
        self.debounced = {}
        self.networks = {}

class model_nvclient(object):
    def __init__(self):
        self._instances = {}
        self._sessions = {}
        self._flavors = {}
        self._images = {}
        self._networks = {}

        self.nova_creds = {}
        self.keystone_creds = {}
        self.session_id = None
        self.username = None
        self.password = None
        self.auth_url = None
        self.project_name = None
        self.sshkey_public = None
        self.sshkey_private = None

