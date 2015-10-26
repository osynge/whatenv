import logging
import config
from ap_common import validate_required
import nvclient_mvc

def manage(args):
    log = logging.getLogger("buildup")
    log.info("debug=%s" % args)
    try:
        validate_required(args,["cfg","state","steering"])
    except argparse.ArgumentError, E:
        log.error(E)
        sys.exit(1)
    cfg = config.cfg()

    if args.cfg:
        cfg.read(args.cfg)

    if args.session_list:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.list_sessions()
        return 0

    if args.instance_list:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.list()
        return 0

    if args.debounce:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.debounce(args.state)

    log.error("No action set")
    return 10

def subparser_manage(subparsers):
    manage_parser = subparsers.add_parser('manage', help='Manage session')
    manage_parser.add_argument('--session-list', action ='store_true',help='list sessions')
    manage_parser.add_argument('--instance-list', action ='store_true',help='list instances')
    manage_parser.add_argument('--debounce', action ='store_true',help='debounce instances')
    manage_parser.set_defaults(
        func=manage,
        description=manage.__doc__,
        help=manage.__doc__,
        )
    return manage_parser
