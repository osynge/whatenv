import novaclient.v1_1.client as nvclient
import logging
import json

from nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient
from nvclient_view_nvclient_connected import view_nvclient_connected
from nvclient_view_nvsession import view_nvsession
from nvclient_view_json import view_instance_json,  view_session_json, view_nvclient_json
import nvclient_view_buildup


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

    def buildup(self, steering):
        config = view_nvsession(self.model_nvclient)
        config.env_apply()
        builder = nvclient_view_buildup.view_buildup(self.model_nvclient)

        builder.connect()
        output = builder.buildup(steering)
        return output
