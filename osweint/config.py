import ConfigParserJson
import os
import logging


class Error(Exception):
    """
    Error
    """

    def __str__(self):
        doc = self.__doc__.strip()
        return ': '.join([doc] + [str(a) for a in self.args])


class cfg(object):
    def __init__(self):
        self.log = logging.getLogger("cfg")

        self.username = os.environ.get('OS_USERNAME')
        self.password = os.environ.get('OS_PASSWORD')
        self.auth_url = os.environ.get('OS_AUTH_URL')
        self.tenant_name = os.environ.get('OS_TENANT_NAME')

    def _validate(self):
        if self.username == None:
            raise Error("No user name specified")

        if self.password == None:
            raise Error("No password specified")
        if self.auth_url == None:
            raise Error("No authurl specified")
        if self.tenant_name == None:
            raise Error("No tenant_name specified")

    def read(self,filename):
        self.cfg = ConfigParserJson.jsonConfigParser()
        self.cfg.read(filename)
        if not self.cfg.has_section("main"):
            self.log.warning("No [main] section found in %s" % (filename))
        if self.cfg.has_option("main", "username"):
            self.username = self.cfg.getJson("main", "username")
        else:
            self.log.warning("No [main] username found in %s" % (filename))
        if self.cfg.has_option("main", "password"):
            self.password = self.cfg.getJson("main", "password")
        else:
            self.log.warning("No [main] password found in %s" % (filename))
        if self.cfg.has_option("main", "auth_url"):
            self.auth_url = self.cfg.getJson("main", "auth_url")
        else:
            self.log.warning("No [main] auth_url found in %s" % (filename))

        if self.cfg.has_option("main", "tenant"):
            self.tenant_name = self.cfg.getJson("main", "tenant")
        else:
            self.log.warning("No [main] tenant found in %s" % (filename))
        self._validate()
    def get_keystone_creds(self):
        self._validate()
        d = {}
        d['username'] = self.username
        d['password'] = self.password
        d['auth_url'] = self.auth_url
        d['tenant_name'] = self.tenant_name
        return d

    def get_nova_creds(self):
        self._validate()
        d = {}
        d['username'] = self.username
        d['api_key'] = self.password
        d['auth_url'] = self.auth_url
        d['project_id'] = self.tenant_name
        return d
