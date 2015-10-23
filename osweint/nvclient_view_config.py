import logging
import sys
import os
from command_runner import Command

LOG = logging.getLogger(__name__)

class view_vmclient_config(object):
    def __init__(self, model):
        self.model = model

    def cfg_apply(self,cfg):
        self.model.username = cfg.username
        self.model.password = cfg.password
        self.model.auth_url = cfg.auth_url
        self.model.project_name = cfg.tenant_name
        try:
            self.model.sshkey_private = os.path.expanduser(cfg.sshkey_private)
        except:
            LOG.info("Defaulting private key to ~/.ssh/id_rsa")
            self.model.sshkey_private = os.path.expanduser("~/.ssh/id_rsa")

        try:
            self.model.sshkey_public = os.path.expanduser(cfg.sshkey_public)
        except:
            LOG.info("Defaulting public key to %s.pub" % (self.model.sshkey_private))
            self.model.sshkey_public = os.path.expanduser("%s.pub" % (self.model.sshkey_private))

        if not os.path.isfile(self.model.sshkey_private):
            cmd = Command('ssh-keygen -b 2048 -t rsa -f %s -q -N ""' % (os.path.expanduser(self.model.sshkey_private)))
            rc, stdout, stderr = cmd.run(20)
            if rc != 0:
                LOG.error("Failed to execute '%s'" % (cmd.cmd))
                LOG.info("%s\n%s\n%s" % (rc, stdout, stderr))
                sys.exit(1)
            self.model.sshkey_public = "%s.pub" % (self.model.sshkey_private)
        if not os.path.isfile(self.model.sshkey_public):
            LOG.error("Cant find '%s'" % (self.model.sshkey_public))
            sys.exit(1)

        with open(self.model.sshkey_public) as f:
            content = f.readlines()
            rawname = str(content[0].strip().split()[2])
            name = ""
            for c in rawname:
                v = ord(c)
                if v in [95,45,43]:
                    name += c
                    continue
                if (90 < v) and (v < 97):
                    name += "-"
                    continue
                if (47 < v) and (v < 58):
                    name += c
                    continue
                if (64 < v) and (v < 123):
                    name += c
                    continue
                name += "-"
                continue

            self.model.sshkey_name = name
            LOG.error("name=%s" % (self.model.sshkey_name))

