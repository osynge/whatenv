import logging
from environ import getenviromentvars
import uuid
from nvclient_model import model_nvsession

class view_nvsession(object):
    def __init__(self, model):
        self.log = logging.getLogger("view.nvsession")
        self.model = model

    def env_apply(self):
        env_var = getenviromentvars()
        env_set_termial = set(["TERMINAL_SSH_CONNECTION",
            "TERMINAL_XAUTHLOCALHOSTNAME",
            "TERMINAL_GPG_TTY"])
        env_set_jenkins = set(["JENKINS_BUILD_TAG",
            "JENKINS_BUILD_URL",
            "JENKINS_EXECUTOR_NUMBER",
            "JENKINS_NODE_NAME",
            "JENKINS_WORKSPACE"])
        env_set_shared = set(["WE_HOSTNAME",
            "WE_USERNAME"])
        shared_set = env_set_shared.intersection(env_var)
        terminal_set = env_set_termial.intersection(env_var)
        jenkins_set = env_set_jenkins.intersection(env_var)
        sessionset = set()
        if len(terminal_set) > 0:
            sessionset.add("TERMINAL")

        if len(jenkins_set) > 0:
            sessionset.add("JENKINS")
        processing_env_set = shared_set.union(terminal_set.union(jenkins_set))
        session_uuid = None
        for session in self.model._sessions:
            if len(self.model._sessions[session].session_type) == 0:
                self.log.error('TODO:account for this state')
            if self.model._sessions[session].session_type != sessionset:
                continue
            session_terminal_set = env_set_termial.intersection(self.model._sessions[session]._md_whenenv)
            if session_terminal_set != terminal_set:
                continue
            session_jenkins_set = jenkins_set.intersection(self.model._sessions[session]._md_whenenv)

            if session_jenkins_set != jenkins_set:
                continue
            thesame = True
            for key in session_terminal_set.union(session_jenkins_set):
                if env_var[key] == self.model._sessions[session]._md_whenenv[key]:
                    continue
                thesame = False
                break
            if not thesame:
                continue
            session_uuid = session
        if session_uuid != None:
             self.model.session_id = session_uuid
             return
        session_uuid = str(uuid.uuid4())
        new_session = model_nvsession()
        new_session.uuid = session_uuid
        new_session.session_type = sessionset
        for key in processing_env_set:
            new_session._md_whenenv[key] = env_var[key]
        self.model._sessions[session_uuid] = new_session
        self.model.session_id = session_uuid

    def env_previous(self):
        self.log.error("Depricated method env_previous")
        return self.get_mattching_keys()

    def get_mattching_sessions(self):
        output = set()
        env_var = getenviromentvars()
        env_set_termial = set(["TERMINAL_SSH_CONNECTION",
            "TERMINAL_XAUTHLOCALHOSTNAME",
            "TERMINAL_GPG_TTY"])
        env_set_jenkins = set(["JENKINS_EXECUTOR_NUMBER",
            "JENKINS_NODE_NAME"])


        terminal_set = env_set_termial.intersection(env_var)
        jenkins_set = env_set_jenkins.intersection(env_var)
        sessionset = set()
        if len(terminal_set) > 0:
            sessionset.add("TERMINAL")

        if len(jenkins_set) > 0:
            sessionset.add("JENKINS")


        for session in self.model._sessions:
            if len(self.model._sessions[session].session_type) == 0:
                self.log.error('TODO:account for this state')
                assert(False)
            if self.model._sessions[session].session_type != sessionset:
                self.log.debug('self.model._sessions[session].session_type=%s' % (self.model._sessions[session].session_type))
                self.log.debug('sessionset=%s' % (sessionset))
                continue
            session_terminal_set = env_set_termial.intersection(self.model._sessions[session]._md_whenenv)
            if session_terminal_set != terminal_set:
                continue
            session_jenkins_set = jenkins_set.intersection(self.model._sessions[session]._md_whenenv)

            if session_jenkins_set != jenkins_set:
                continue
            thesame = True
            for key in session_terminal_set.union(session_jenkins_set):
                if env_var[key] == self.model._sessions[session]._md_whenenv[key]:
                    continue
                thesame = False
                break
            if not thesame:
                continue
            output.add(session)
        return output

