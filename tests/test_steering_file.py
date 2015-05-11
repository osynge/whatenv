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
from osweint.nvclient_view_buildup import view_buildup
from osweint.nvclient_view_buildup import Error as Error_view_buildup

class TestSteering(unittest.TestCase):
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
        log = logging.getLogger("TestSteering.tearDown")
        session = self.connection.get_session_current()
        if (session != None):
            log.error("session = %s" % (session))
            instances = self.connection.list_instance_id(session)
            log.error("instances = %s" % (instances))
            self.connection.delete_instance_id(instances)


    def test_view_empty_file(self):
        log = logging.getLogger("TestSteering.view_empty_file")
        builder = view_buildup(self.mclient)
        try:
            builder.enstantiate("/dev/null",self.connection)
        except Error_view_buildup, e:
            log.debug("Exception=%s" % ( e))
            return
        assert (False)
    def test_view_unparsable_file(self):
        log = logging.getLogger("TestSteering.view_empty_file")
        builder = view_buildup(self.mclient)
        try:
            builder.enstantiate("/etc/fstab",self.connection)
        except Error_view_buildup, e:
            log.debug("Exception=%s" % ( e))
            return
        assert (False)
    
    def test_view_parsable_file(self):
        log = logging.getLogger("TestSteering.view_empty_file")
        builder = view_buildup(self.mclient)
        builder.enstantiate("steering_example.json",self.connection)
        
        
        
        
if __name__ == "__main__":
    logging.basicConfig()
    LoggingLevel = logging.WARNING
    logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    
    import nose


    
    
    
    nose.runmodule()
