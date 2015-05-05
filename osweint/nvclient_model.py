


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
        self.uuid = None
        self.os_name = None
        self.ipv4 = None


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


class model_instance(object):
    def __init__(self):
        self._md_whenenv = {}
        self._md_user = {}
        self.os_id = None
        self.os_imageid = None
        self.os_name = None
        self.os_image_human_name = None
        self.sessions = set()



class model_nvclient(object):
    def __init__(self):
        self._instances = {}
        self._sessions = {}
        self._flavors = {}
        self._images = {}
        
        self.nova_creds = {}
        self.keystone_creds = {}
        self.session_id = None



