import logging
from ap_common import validate_required



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
