import logging
import json

from nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient
from nvclient_view_nvclient_connected import view_nvclient_connected
import nvclient_view_nvsession
from nvclient_view_json import view_instance_json,  view_session_json, view_nvclient_json
import nvclient_view_buildup
import nvclient_view_debounce

import nvclient_view_con
import types

class Error(Exception):
    """
    Error
    """

    def __str__(self):
        doc = self.__doc__.strip()
        return ': '.join([doc] + [str(a) for a in self.args])


def filter_metadata(metadata, filter_obj):
    for key in filter_obj:
        if not key in metadata:
            return False
        value_type = type(filter_obj[key])
        if value_type is types.IntType:
            if metadata[key] != filter_obj[key]:
                return False
        if value_type is types.UnicodeType:
            if metadata[key] != filter_obj[key]:
                return False
        if value_type is types.ListType:
            for list_index in range(0,len(filter_obj[key])):
                list_item = filter_obj[key][list_index]
                list_item_type = type(list_item)
                if list_item_type is types.IntType:
                    if not list_item in metadata[key]:
                        return False
                if list_item_type is types.UnicodeType:
                    if not list_item in metadata[key]:
                        return False

        if type(metadata[key]) != type(filter_obj[key]):
            return False

    return True


class view_delete(nvclient_view_con.view_nvclient_con):
    def __init__(self, model):
        nvclient_view_con.view_nvclient_con.__init__(self,model)
        self.log = logging.getLogger("view.instance")

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
        self.model.username = cfg.username
        self.model.password = cfg.password
        self.model.auth_url = cfg.auth_url
        self.model.project_name = cfg.tenant_name


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
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        config.env_apply()
        outputer = view_nvclient_json(self.model_nvclient)
        print json.dumps(outputer.list_images_default() , sort_keys=True, indent=4)


    def list_sessions(self):
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        config.env_apply()
        outputer = view_nvclient_json(self.model_nvclient)
        print json.dumps(outputer.list_sessions_default() , sort_keys=True, indent=4)

    def delete_session(self):
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        config.env_apply()
        deleter = view_delete(self.model_nvclient)
        deleter.connect()
        deleter.session_by_weid(self.model_nvclient.session_id)

    def delete_session_all(self):
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        config.env_apply()
        deleter = view_delete(self.model_nvclient)
        deleter.connect()
        for session in self.model_nvclient._sessions:
            deleter.session_by_weid(session)

    def sessions_get_previous(self):
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        return config.env_previous()

    def buildup(self, steering):
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        previous_sessions = config.env_previous()
        deleter = view_delete(self.model_nvclient)
        deleter.connect()
        for session_2_del in previous_sessions:
            deleter.session_by_weid(session_2_del)
        config.env_apply()
        builder = nvclient_view_buildup.view_buildup(self.model_nvclient)

        builder.connect()
        try:
            output = builder.buildup(steering)
        except nvclient_view_buildup.Error, E:
            error_text = ''.join([str(a) for a in E.args])
            raise Error(error_text)
        return output
    def debounce(self, state):
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        config.env_apply()
        builder = nvclient_view_debounce.view_buildup(self.model_nvclient)

        builder.connect()
        output = builder.debounce(state)
        return output
    def state_load(self,state):
        fp = open(state)
        json_loaded = json.load(fp)
        fp.close()
        loader = view_nvclient_json(self.model_nvclient)
        loader.load_sessions_default(json_loaded)
    def filter_instances(self,label_filter):
        config = nvclient_view_nvsession.view_nvsession(self.model_nvclient)
        previous_sessions = config.env_previous()
        print previous_sessions
        matching = []
        json_loaded = json.loads(label_filter)
        output = set()
        for key in  self.model_nvclient._instances.keys():
            labels = self.model_nvclient._instances[key]._md_user
            if filter_metadata(labels,json_loaded):
                output.add(key)
        for item in output:
            print item
