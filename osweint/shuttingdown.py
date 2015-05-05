import optparse
import logging
import sys
from __version__ import version
import config
import nvclient_mvc



def main():

    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-L', '--logcfg', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-v', '--verbose', action ='count',help='Change global log level, increasing log output.', metavar='LOGFILE')
    p.add_option('-q', '--quiet', action ='count',help='Change global log level, decreasing log output.', metavar='LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Configuration file.', metavar='CFG_FILE')
    p.add_option('--state', action ='store',help='State file')
    p.add_option('--all', action ='store_true',help='teardown all VM')
    p.add_option('--bysession', action ='store_true',help='LEGACY:shutdown vms by session')
    p.add_option('--cfg', action ='store',help='osweint settings')
    p.add_option('--instance-list', action ='store_true',help='list instances')
    p.add_option('--session-list', action ='store_true',help='list sessions')
    p.add_option('--session-del', action ='store_true',help='tear all VM for this session')
    p.add_option('--filter-state', action ='store',help='Extract information from json')
    p.add_option('--session', action ='store',help='Extract information from json')
    
    logFile = None
    input_file = None
    output_file = None
    label_filter = None
    session = None
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
        requires.add("cfg")

    if options.bysession:
        actions.add("session_del")
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

    if options.session:
        input_file = options.session
        provides.add("session")

    if options.filter_state:
        label_filter = options.filter_state
        actions.add("filter_state")
        requires.add("state")

    if len(actions) == 0:
        log.error('No task selected')
        sys.exit(1)

    extra_deps = provides.difference(requires)
    missing_deps = requires.difference(provides)

    if len(extra_deps):
        for dep in extra_deps:
            log.warning('Extra paramter:%s' %  (dep))
    if len(missing_deps):
        for dep in missing_deps:
            log.error('Missing paramter:%s' %  (dep))
        sys.exit(1)


    if "all" in actions:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.delete_session_all()

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
        if session == None:
            session = controler.get_current_session()
        controler.delete_session(session)
        
    if len(missing_deps):
        for dep in missing_deps:
            log.error('Missing paramter:%s' %  (dep))
        sys.exit(1)


    if "all" in actions:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.delete_session_all()

    if "list" in actions:

        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
    if "filter_state" in actions:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.state_load(input_file)
        controler.filter_instances(label_filter)
    return
if __name__ == "__main__":
    main()
