import sys, os
sys.path = [os.path.abspath(os.path.dirname(os.path.dirname(__file__)))] + sys.path

import logging
import unittest
import uuid


    
from osweint.nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient
from osweint.nvclient_view_nvclient_connected import view_nvclient_connected as view_nvclient_connected
from osweint.nvclient_view_nvclient_connected import view_nvclient_connected
from osweint.nvclient_view_config import view_vmclient_config
import osweint.config


class TestLaunch(unittest.TestCase):
    def setUp(self):
        self.mclient = model_nvclient()
        config = view_vmclient_config(self.mclient)
        config_data= osweint.config.cfg()
        config_data.read("osweint.cfg")
        config.cfg_apply(config_data)
        self.connection = view_nvclient_connected(self.mclient)
        self.connection.connect()
        self.connection.update()
        
    def tearDown(self):
        log = logging.getLogger("TestLaunch.tearDown")
        session_id = self.connection.get_session_current()
        if session_id == None:
            return
        instances = self.connection.list_instance_id(session_id)
        log.error("instances = %s" % (instances))
        metadata = self.connection.delete_instance_id(instances)


    def test_can_boot_data_min(self):
        log = logging.getLogger("test_connect_current_session_can_boot")
        session_id = self.connection.create_session(str(uuid.uuid4()))
        self.connection.update()
        instance_id = self.connection.create_instance(str(uuid.uuid4()),session_id)
        metadata = self.connection.gen_metadata(instance_id)
        assert ("WE_SESSION" in metadata.keys())
        assert ("WE_USERNAME" in metadata.keys())
        assert ("WE_HOSTNAME" in metadata.keys())
        assert ("WE_ID" in metadata.keys())
    
    
    def test_read_current_sessions(self):
        log = logging.getLogger("test_read_current_sessions")
        for session_id in self.mclient._sessions.keys():
            instance_list = self.connection.list_instance_id(session_id)
            for instance in instance_list:
                metadata = self.connection.gen_metadata(instance)
                log.error("session=%s , instance=%s ,metadata=%s" % (session_id,instance,metadata))
        
if __name__ == "__main__":
    logging.basicConfig()
    LoggingLevel = logging.WARNING
    logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    
    import nose


    
    
    
    nose.runmodule()
