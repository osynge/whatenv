import logging
import config
from ap_common import validate_required
import nvclient_mvc

def buildup(args):
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


    if args.start:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        try:
            controler.buildup(args.steering)
            controler.state_store(args.state)
        except nvclient_mvc.Error, E:
            log.error(E)
            sys.exit(1)



    log.error("No action set")
    return 10
def subparser_buildup(subparsers):
    buildup_parser = subparsers.add_parser('buildup', help='Build session')
    buildup_parser.add_argument('--start', action ='store_true',help='start session')
    buildup_parser.set_defaults(
        func=buildup,
        description=buildup.__doc__,
        help=buildup.__doc__,
        )
    return buildup_parser
