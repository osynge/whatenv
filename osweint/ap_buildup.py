import logging
from ap_common import validate_required

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
