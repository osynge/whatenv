import argparse
import logging
import sys
from __version__ import version
import config
import nvclient_mvc

from textwrap import dedent



def validate_required(args,required):
    log = logging.getLogger("validate_required")
    if "steering" in required:
        if args.steering == None:
            raise argparse.ArgumentError(None, "steering file missing")
    if "cfg" in required:
        if args.cfg == None:
            raise argparse.ArgumentError(None, "cfg file missing")
    if "state" in required:
        if args.state == None:
            raise argparse.ArgumentError(None, "state file missing")


def buildup(args):
    log = logging.getLogger("buildup")
    log.info("debug=%s" % args)
    try:
        validate_required(args,["cfg","state","steering"])
    except argparse.ArgumentError, E:
        log.error(E)
        sys.exit(1)

def subparser_buildup(subparsers):
    buildup_parser = subparsers.add_parser('buildup', help='Build session')
    buildup_parser.set_defaults(
        func=buildup,
        description=buildup.__doc__,
        help=buildup.__doc__,
        )
    return buildup_parser

def manage(args):
    log = logging.getLogger("buildup")
    log.info("debug=%s" % args)
    try:
        validate_required(args,["cfg","state","steering"])
    except argparse.ArgumentError, E:
        log.error(E)
        sys.exit(1)

def subparser_manage(subparsers):
    manage_parser = subparsers.add_parser('manage', help='Manage session')
    manage_parser.add_argument('--session-list', action ='store_true',help='list sessions')
    manage_parser.add_argument('--instance-list', action ='store_true',help='list instances')
    manage_parser.set_defaults(
        func=manage,
        description=manage.__doc__,
        help=manage.__doc__,
        )
    return manage_parser

def teardown(args):
    log = logging.getLogger("buildup")
    log.info("debug=%s" % args)
    try:
        validate_required(args,["cfg","state","steering"])
    except argparse.ArgumentError, E:
        log.error(E)
        sys.exit(1)

def subparser_teardown(subparsers):
    teardown_parser = subparsers.add_parser('teardown', help='Teardown session')
    teardown_parser.add_argument('--all', action ='store_true',help='teardown all VM')
    teardown_parser.add_argument('--bysession', action ='store_true',help='LEGACY:shutdown vms by session')
    teardown_parser.set_defaults(
        func=teardown,
        description=teardown.__doc__,
        help=teardown.__doc__,
        )
    return teardown_parser

def parser_get():
    p = argparse.ArgumentParser(version = version)
    subparsers = p.add_subparsers(dest="subparser_name")
    
    subparser_buildup(subparsers)
    subparser_manage(subparsers)
    subparser_teardown(subparsers)
    
    p.add_argument('-L', '--logcfg', action ='store',help='Logfile configuration file.')
    p.add_argument('-V', '--verbose', action ='count',help='Change global log level, increasing log output.')
    p.add_argument('-q', '--quiet', action ='count',help='Change global log level, decreasing log output.')
    p.add_argument('-C', '--config-file', action ='store',help='Configuration file.')
    p.add_argument('--cfg', action ='store',help='osweint settings')
    p.add_argument('--session', action ='store',help='Extract information from json')
    p.add_argument('--steering', action ='store',help='Steering file to create VM')
    p.add_argument('--state', action ='store',help='State file to generate / update.')
    return p

def logging_setup(args):
    logFile = None
    LoggingLevel = logging.INFO
    LoggingLevelCounter = 2
    if args.verbose:
        LoggingLevelCounter = LoggingLevelCounter - args.verbose
        if args.verbose == 1:
            LoggingLevel = logging.INFO
        if args.verbose == 2:
            LoggingLevel = logging.DEBUG
    if args.quiet:
        LoggingLevelCounter = LoggingLevelCounter + args.quiet
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

    if args.logcfg:
        logFile = args.log_config
    if logFile != None:
        if os.path.isfile(str(args.log_config)):
            logging.config.fileConfig(args.log_config)
        else:
            logging.basicConfig(level=LoggingLevel)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (args.log_config))
            sys.exit(1)
    else:
        logging.basicConfig(level=LoggingLevel)

def main():
    """Runs program and handles command line options"""
    p = parser_get()
    args = p.parse_args()
    logging_setup(args)
    args.func(args)
    
    
    sys.exit(1)
    
    
    input_file = None
    output_file = None
    steering_file = None
    label_filter = None
    session = None
    actions = set()
    requires = set()
    provides = set()

    cfg = config.cfg()

    options, arguments = p.parse_args()
    # Set up log file
    
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

    if options.steering:
        steering_file = options.steering
        provides.add("steering")


    if options.buildup:
        actions.add("buildup")
        requires.add("steering")
        requires.add("state")
        requires.add("cfg")
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
