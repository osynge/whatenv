import novaclient.v1_1.client as nvclient
import json
from environ import getenviromentvars
import optparse
import logging
import sys
from __version__ import version
import config
import nvclient_mvc


def sever_list_clear(cfg):
    log = logging.getLogger("teardown.all")
    creds = cfg.get_nova_creds()
    nova = nvclient.Client(**creds)
    server_list = nova.servers.list()
    for server in server_list:
        log.debug("prcessing:%s" % (server.id))
        if server.name[:8] == "whenenv-":
            log.debug("deleting:%s" % (server.name))
            server.delete()

def shuttdown_by_id(cfg,catalogue,ident):
    log = logging.getLogger("teardown.id")
    #print ident
    #print catalogue[ident]
    creds = cfg.get_nova_creds()
    nova = nvclient.Client(**creds)
    server_list = nova.servers.list()
    for server in server_list:
        #print "prcessing:%s" % (server.id)
        if server.id == catalogue[ident]['OS_ID']:
            log.debug("deleting:%s" % (server.name))
            server.delete()
            log.debug("server.status:%s" % (server.status))
def read_input(filename):
    f = open(filename)
    json_string = f.read()
    loadedfile = json.loads(json_string)
    return loadedfile



def process_actions(cfg,input_name):
    env_set_termial = set(["TERMINAL_SSH_CONNECTION",
        "TERMINAL_XAUTHLOCALHOSTNAME",
        "TERMINAL_GPG_TTY"])
    env_set_jenkins = set(["JENKINS_BUILD_TAG",
        "JENKINS_BUILD_URL",
        "JENKINS_EXECUTOR_NUMBER",
        "JENKINS_NODE_NAME",
        "JENKINS_WORKSPACE"])
    
    env_var = getenviromentvars()
    terminal_use = False
    jenkins_use = False
    terminal_set = env_set_termial.intersection(env_var)
    jenkins_set = env_set_jenkins.intersection(env_var)
    if len(terminal_set) > 0:
        terminal_use = True
    if len(jenkins_set) > 0:
        jenkins_use = True

    matchset = set()
    if terminal_use:
        matchset = matchset.union(env_set_termial)
    if jenkins_use:
        matchset = matchset.union(env_set_jenkins)
    
    output_data = read_input(input_name)
    delete_set = set()
    for key in output_data:
        contnent = output_data[key].keys()
        keys_intersection = matchset.intersection(contnent)
        if len(keys_intersection) == 0:
            continue
        difference = False
        for intersect in keys_intersection:
            env_data = env_var[intersect]
            db_data = output_data[key][intersect]
            if (env_data == db_data):
                
                continue
            print intersect, env_data
            difference = True
        if not difference:
            delete_set.add(key)
    for todel in delete_set:
        shuttdown_by_id(cfg, output_data, todel)
            

def main():
    
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logcfg', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-v', '--verbose', action ='count',help='Change global log level, increasing log output.', metavar='LOGFILE')
    p.add_option('-q', '--quiet', action ='count',help='Change global log level, decreasing log output.', metavar='LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Configuration file.', metavar='CFG_FILE')
    p.add_option('--state', action ='store',help='State file')
    p.add_option('--all', action ='store_true',help='teardown all VM')
    p.add_option('--bysession', action ='store_true',help='tear down VM for this session')
    p.add_option('--cfg', action ='store',help='Openstack settings')
    p.add_option('--instance-list', action ='store_true',help='tear down VM for this session')
    p.add_option('--session-list', action ='store_true',help='tear down VM for this session')
    p.add_option('--session-del', action ='store_true',help='tear down VM for this session')
    logFile = None
    input_file = None
    output_file = None
    actions = set()
    requires = set()
    provides = set()
    
    cfg = config.cfg()
    
    options, arguments = p.parse_args()
    # Set up log file
    LoggingLevel = logging.WARNING
    LoggingLevelCounter = 2
    if options.verbose:
        LoggingLevelCounter = LoggingLevelCounter - options.verbose
        if options.verbose == 1:
            LoggingLevel = logging.INFO
        if options.verbose == 2:
            LoggingLevel = logging.DEBUG
    if options.quiet:
        LoggingLevelCounter = LoggingLevelCounter + options.quiet
    if LoggingLevelCounter <= 0:
        LoggingLevel = logging.DEBUG
    if LoggingLevelCounter == 1:
        LoggingLevel = logging.INFO
    if LoggingLevelCounter == 2:
        LoggingLevel = logging.WARNING
    if LoggingLevelCounter == 3:
        LoggingLevel = logging.ERROR
    if LoggingLevelCounter == 4:
        LoggingLevel = logging.FATAL
    if LoggingLevelCounter >= 5:
        LoggingLevel = logging.CRITICAL

    if options.logcfg:
        logFile = options.log_config
    if logFile != None:
        if os.path.isfile(str(options.log_config)):
            logging.config.fileConfig(options.log_config)
        else:
            logging.basicConfig(level=LoggingLevel)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.log_config))
            sys.exit(1)
    else:
        logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    
    if options.cfg:
        cfg.read(options.cfg)
        provides.add("cfg")
        
    if options.all:
        actions.add("all")
        requires.add("state")
        requires.add("cfg")

    if options.bysession:
        actions.add("bysession")
        requires.add("state")
        requires.add("cfg")
        
    if options.instance_list:
        actions.add("list")
        requires.add("cfg")

    if options.session_list:
        actions.add("list_session")
        requires.add("cfg")

    if options.session_del:
        actions.add("session_del")
        requires.add("cfg")

    if options.state:
        input_file = options.state
        provides.add("state")
    
    extra_deps = provides.difference(requires)
    missing_deps = requires.difference(provides)
    
    if len(extra_deps):
        for dep in extra_deps:
            log.warning('Missing paramter:%s' %  (dep))
    if len(missing_deps):
        for dep in missing_deps:
            log.error('Missing paramter:%s' %  (dep))
        sys.exit(1)
    
    
    if "all" in actions:
        sever_list_clear(cfg)
        sys.exit (0)
    if "bysession" in actions:
        process_actions(cfg, str(input_file))
    
    
    if "list" in actions:
        
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.list()
    if "list_session" in actions:
        
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.list_sessions()
        
    if "session_del" in actions:
        
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.delete_session()
    
    return 
if __name__ == "__main__":
    main() 
