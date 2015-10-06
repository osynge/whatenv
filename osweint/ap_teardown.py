import logging
import config
from ap_common import validate_required
import nvclient_mvc

def teardown(args):
    log = logging.getLogger("buildup")
    log.info("debug=%s" % args)
    try:
        validate_required(args,["cfg"])
    except argparse.ArgumentError, E:
        log.error(E)
        sys.exit(1)

    cfg = config.cfg()

    if args.cfg:
        cfg.read(args.cfg)

    if args.all:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.delete_session_all()
        return 0

    if args.bysession:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        if args.session == None:
            session = controler.get_current_session()
            log.info("Defaulting session as '%s'" % (session))
        controler.delete_session(session)
        return 0

    log.error("No action set")
    return 10

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
