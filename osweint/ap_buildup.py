import logging
import config
from ap_common import validate_required
import nvclient_mvc
import argparse
import sys

from osweint.nvclient_model import model_nvsession, model_nvnetwork, model_instance, model_nvclient
from osweint.nvclient_view_config import view_vmclient_config
import osweint.config
from osweint.nvclient_view_nvclient_connected import view_nvclient_connected
from osweint.nvclient_view_buildup import view_buildup
from osweint.nvclient_view_buildup import Error as Error_view_buildup


def buildup(args):
    log = logging.getLogger("buildup")
    log.info("debug=%s" % args)
    try:
        validate_required(args,["cfg","state","steering"])
    except argparse.ArgumentError, E:
        log.error(E)
        sys.exit(1)
    sessionId = None


    if args.session:
        sessionId = args.session



    if args.start:
        mclient = model_nvclient()
        config = view_vmclient_config(mclient)
        config_data = osweint.config.cfg()
        config_data.read(args.cfg)
        config.cfg_apply(config_data)
        connection = view_nvclient_connected(mclient)
        connection.connect()
        connection.update()
        builder = view_buildup(mclient)
        builder.enstantiate(args.steering,connection)
        connection.update()
        connection.persist(args.state)

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
