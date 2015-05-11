import sys, os
sys.path = [os.path.abspath(os.path.dirname(os.path.dirname(__file__)))] + sys.path

import logging
import unittest
import uuid


import nose

from osweint.nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient

from osweint.nvclient_view_nvclient_connected import view_nvclient_connected as view_nvclient_connected
from osweint.nvclient_view_nvclient_connected import view_nvclient_connected
from osweint.nvclient_view_config import view_vmclient_config
import osweint.config


class TestSession(unittest.TestCase):
    def setUp(self):
        mclient = model_nvclient()
        config = view_vmclient_config(mclient)
        config_data= osweint.config.cfg()
        config_data.read("osweint.cfg")
        config.cfg_apply(config_data)
        self.connection = view_nvclient_connected(mclient)
        self.connection.connect()
    def tearDown(self):
        pass
    
    def test_connection_update(self):
        self.connection.update()

    def test_connect_list_sessions_empty(self):
        frog = self.connection.list_sessions_ids()
        assert (frog != None)
        assert (len(frog) == 0)
    def test_connect_list_sessions_can_add(self):
        frog = self.connection.list_sessions_ids()
        assert (frog != None)
        assert (len(frog) == 0)
        
        snake = self.connection.list_sessions_ids()
        
    def test_connect_list_sessions_can_fill(self):
        self.connection.update()
        frog = self.connection.list_sessions_ids()
        
        assert (frog != None)
        for skey_session in frog:
            instance_list = self.connection.list_instance_id(skey_session)
            assert (instance_list != None)
            assert (len(instance_list) != 0)


    def test_connect_current_session_can_add(self):
        self.connection.update()
        session_id = self.connection.create_session(str(uuid.uuid4()))
        instance_list = self.connection.list_instance_id(session_id)
        assert (instance_list != None)
        assert (len(instance_list) == 0)
        
        instance_id = self.connection.create_instance(str(uuid.uuid4()), session_id)
        instance_list = self.connection.list_instance_id(session_id)
        assert (instance_list != None)
        assert (len(instance_list) == 1)
        

    def test_connect_current_session_can_gen_metadata(self):
        log = logging.getLogger("test_connect_current_session_can_add22")
        
        session_id = str(uuid.uuid4())
        instance_id = str(uuid.uuid4())
        
        session_id = self.connection.create_session(session_id)
        instance_list = self.connection.list_instance_id(session_id)
        assert (instance_list != None)
        assert (len(instance_list) == 0)
        instance_id = self.connection.create_instance(instance_id,session_id)
        
        assert (instance_id != None)
        instnace_length = int(len(instance_id))
        log.error("fred=%s" % (instnace_length))
        assert (len(instance_id) == 36)
        
        metadata = self.connection.gen_metadata(instance_id)
        log.error(metadata)
        
    def test_connect_current_session_can_del(self):
        self.connection.update()
        session_id = self.connection.create_session(str(uuid.uuid4()))
        instance_list = self.connection.list_instance_id(session_id)
        assert (instance_list != None)
        assert (len(instance_list) == 0)
        instance_id = self.connection.create_instance(str(uuid.uuid4()),session_id)
        instance_list = self.connection.list_instance_id(session_id)
        
        
        
        assert (instance_list != None)
        assert (len(instance_list) == 1)
        
        self.connection.delete_instance_id([instance_id])
        instance_list = self.connection.list_instance_id(session_id)
        assert (instance_list != None)
        assert (len(instance_list) == 0)



    def test_sessions_create(self):
        frog = self.connection.list_sessions_ids()
        
        assert (frog != None)
        assert (len(frog) == 0)
        new_id = str(uuid.uuid4())
        session_id = self.connection.create_session(new_id)
        assert (session_id == new_id)
        
        snake = self.connection.list_sessions_ids()
        
        assert (snake != None)
        assert (len(snake) == 1)
        
        for skey_session in frog:
            instance_list = self.connection.list_instance_id(skey_session)
            assert (instance_list != None)
            assert (len(instance_list) != 0)









if __name__ == "__main__":
    logging.basicConfig()
    LoggingLevel = logging.WARNING
    logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")


    
    
    
    nose.runmodule()
