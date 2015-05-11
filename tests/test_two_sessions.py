import sys, os
sys.path = [os.path.abspath(os.path.dirname(os.path.dirname(__file__)))] + sys.path

import logging
import unittest
import uuid
import time

    
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
        session_id = self.connection.create_session(self.session1)
        assert (session_id == self.session1)
        session_id = self.connection.create_session(self.session2)
        assert (session_id == self.session2)
        self.clear_session()
        
    def tearDown(self):
        time.sleep(30)
        self.clear_session()
        
    def clear_session(self):
        log = logging.getLogger("TestTwoSession.clear_session")
        instances1 = set()
        self.connection.update()
        session_id = self.connection.get_session_current()
        if session_id != None:
            instances1 = self.connection.list_instance_id(session_id)
        instances2 = self.connection.list_instance_id(self.session1)
        instances3 = self.connection.list_instance_id(self.session2)
        instances_all = instances1.union(instances2).union(instances3)
        log.error("instances = %s" % (instances_all))
        metadata = self.connection.delete_instance_id(instances_all)


    def test_connect_current_session_can_boot_session1(self):
        self.connection.update()
        instance_id = self.connection.create_instance(str(uuid.uuid4()),self.session1)
        assert (instance_id != None)
        instance_list = self.connection.list_instance_id(self.session1)
        assert (instance_list != None)
        assert (len(instance_list) == 1)
        flavor_list = self.connection.list_flavor_id()
        assert (flavor_list != None)
        assert (len(flavor_list) > 1)
        self.connection.update()
        
        flavor_list = self.connection.list_flavor_id()
        
        
        instance_list = self.connection.list_instance_id(self.session1)
        
        assert (instance_list != None)
        assert (len(instance_list) == 1)
        flavor_list = self.connection.list_flavor_id()
        assert (flavor_list != None)
        #log.error("flavor_list = %s" % (flavor_list))
        flavour_id = flavor_list.pop()
        
        
        images_list = self.connection.list_images_id()
        images_id = images_list.pop()
        metadata = self.connection.gen_metadata(instance_id)
        #log.error("gen_metadata = %s" % (metadata))
        metadata["OS_IMAGE_NAME"] = "SLES12" 
        metadata["OS_FLAVOR_NAME"] = "m1.large"
        metadata["OS_FLAVOR_ID"] = "ss"
        metadata["OS_NAME"] = "m1.tindfdfdy"
        metadata["OS_IMAGE_HUMAN_NAME"] = "m1.sdsdsdsds"
        metadata["WE_TYPE_UUID"] = "m1.tsdsdsdiny"
        
        
        self.connection.add_metadata(instance_id,metadata)
        result = self.connection.boot_instance(instance_id,images_id,flavour_id)
        assert (instance_id == result)
        instance_list = self.connection.list_instance_id(self.session1)
        assert (instance_id in instance_list)
        self.connection.delete_instance_id([instance_id])
        instance_list = self.connection.list_instance_id(self.session1)
        assert (instance_list != None)
        assert (len(instance_list) == 0)
        assert (not instance_id in instance_list)


    def test_connect_current_session_can_boot_session2(self):
        self.connection.update()
        instance_id = self.connection.create_instance(str(uuid.uuid4()),self.session2)
        assert (instance_id != None)
        instance_list = self.connection.list_instance_id(self.session2)
        assert (instance_list != None)
        assert (len(instance_list) == 1)
        flavor_list = self.connection.list_flavor_id()
        assert (flavor_list != None)
        assert (len(flavor_list) > 1)
        self.connection.update()
        
        flavor_list = self.connection.list_flavor_id()
        
        
        instance_list = self.connection.list_instance_id(self.session2)
        
        assert (instance_list != None)
        assert (len(instance_list) == 1)
        flavor_list = self.connection.list_flavor_id()
        assert (flavor_list != None)
        #log.error("flavor_list = %s" % (flavor_list))
        flavour_id = flavor_list.pop()
        
        
        images_list = self.connection.list_images_id()
        images_id = images_list.pop()
        metadata = self.connection.gen_metadata(instance_id)
        #log.error("gen_metadata = %s" % (metadata))
        metadata["OS_IMAGE_NAME"] = "SLES12" 
        metadata["OS_FLAVOR_NAME"] = "m1.large"
        metadata["OS_FLAVOR_ID"] = "ss"
        metadata["OS_NAME"] = "m1.tindfdfdy"
        metadata["OS_IMAGE_HUMAN_NAME"] = "m1.sdsdsdsds"
        metadata["WE_TYPE_UUID"] = "m1.tsdsdsdiny"
        
        
        self.connection.add_metadata(instance_id,metadata)
        result = self.connection.boot_instance(instance_id,images_id,flavour_id)
        assert (instance_id == result)
        instance_list = self.connection.list_instance_id(self.session2)
        assert (instance_id in instance_list)
        self.connection.delete_instance_id([instance_id])
        instance_list = self.connection.list_instance_id(self.session2)
        assert (instance_list != None)
        assert (len(instance_list) == 0)
        assert (not instance_id in instance_list)


if __name__ == "__main__":
    logging.basicConfig()
    LoggingLevel = logging.WARNING
    logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    import nose


    
    
    
    nose.runmodule()
