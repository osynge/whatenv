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


class TestTwoSession(unittest.TestCase):
    def setUp(self):
        self.mclient = model_nvclient()
        config = view_vmclient_config(self.mclient)
        config_data= osweint.config.cfg()
        config_data.read("osweint.cfg")
        config.cfg_apply(config_data)
        self.connection = view_nvclient_connected(self.mclient)
        self.connection.connect()
        self.connection.update()
        self.session1 = str(uuid.uuid4())
        self.session2 = str(uuid.uuid4())
        
    def tearDown(self):
        log = logging.getLogger("TestLaunch.tearDown")
        session = self.connection.get_session_current()
        assert (session != None)
        log.error("session = %s" % (session))
        instances = self.connection.list_instance_id(session)
        log.error("instances = %s" % (instances))
        #self.connection.delete_instance_id(instances)


    def test_can_find_session(self):
        log = logging.getLogger("main")
        initallength = len(self.mclient._sessions)
        log.error("initallength = %s" % (initallength))
        session = self.connection.get_session_current()
        log.error("session = %s" % (session))
        assert (session != None)
        
if __name__ == "__main__":
    logging.basicConfig()
    LoggingLevel = logging.WARNING
    logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    import nose


    
    
    
    nose.runmodule()
