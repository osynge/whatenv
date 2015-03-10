import os
import sys
import optparse
import logging
from __version__ import version
import nvclient_mvc
import config


def main():

    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logcfg', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-v', '--verbose', action ='count',help='Change global log level, increasing log output.', metavar='LOGFILE')
    p.add_option('-q', '--quiet', action ='count',help='Change global log level, decreasing log output.', metavar='LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Configuration file.', metavar='CFG_FILE')
    p.add_option('--state', action ='store',help='State file')
    p.add_option('--cfg', action ='store',help='Openstack settings')
    p.add_option('--prototype', action ='store_true',help='Openstack settings')
    p.add_option('--legacy', action ='store_true',help='Openstack settings')
    logFile = None
    file_state = None
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

    if options.state:
        file_state = options.state
        provides.add("state")

    if options.legacy:
        actions.add("legacy")
        requires.add("state")

    if options.prototype:
        actions.add("prototype")
        requires.add("cfg")
        requires.add("state")

    if len(actions) == 0:
        actions.add("legacy")
        requires.add("state")
        
    extra_deps = provides.difference(requires)
    missing_deps = requires.difference(provides)

    if len(extra_deps):
        for dep in extra_deps:
            log.warning('Missing paramter:%s' %  (dep))
    if len(missing_deps):
        for dep in missing_deps:
            log.error('Missing paramter:%s' %  (dep))
        sys.exit(1)

    if "legacy" in actions:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.debounce(file_state)

    if "prototype" in actions:
        controler = nvclient_mvc.controler()
        controler.read_config(cfg)
        controler.connect()
        controler.debounce(file_state)


    return
if __name__ == "__main__":
    main()
