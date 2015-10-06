import logging
import argparse

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
