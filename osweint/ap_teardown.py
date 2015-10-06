import logging
from ap_common import validate_required


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
