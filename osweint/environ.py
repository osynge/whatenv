import os




def getenviromentvars():
    metadata = {}
    session_id =  os.environ.get('BUILD_TAG')
    if session_id:
        metadata['JENKINS_BUILD_TAG'] = session_id
    session_id =  os.environ.get('NODE_NAME')
    if session_id:
        metadata['JENKINS_NODE_NAME'] = session_id
    session_id =  os.environ.get('WORKSPACE')
    if session_id:
        metadata['JENKINS_WORKSPACE'] = session_id
    session_id =  os.environ.get('BUILD_URL')
    if session_id:
        metadata['JENKINS_BUILD_URL'] = session_id
    session_id =  os.environ.get('JENKINS_URL ')
    if session_id:
        metadata['JENKINS_JENKINS_URL '] = session_id
    session_id =  os.environ.get('JENKINS_JAVA_HOME')
    if session_id:
        metadata['JENKINS_JENKINS_JAVA_HOME'] = session_id
    session_id =  os.environ.get('EXECUTOR_NUMBER')
    if session_id:
        metadata['JENKINS_EXECUTOR_NUMBER'] = session_id

    session_id =  os.environ.get('XAUTHLOCALHOSTNAME')
    if session_id:
        metadata['TERMINAL_XAUTHLOCALHOSTNAME'] = session_id
    session_id =  os.environ.get('USER')
    if session_id:
        metadata['WE_USERNAME'] = session_id
    session_id =  os.environ.get('GPG_TTY')
    if session_id:
        metadata['TERMINAL_GPG_TTY'] = session_id
    session_id =  os.environ.get('SSH_CONNECTION')
    if session_id:
        metadata['TERMINAL_SSH_CONNECTION'] = session_id
    session_id =  os.environ.get('HOSTNAME')
    if session_id:
        metadata['WE_HOSTNAME'] = session_id

    return metadata
