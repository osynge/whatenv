import novaclient.v1_1.client as nvclient
from credentials import get_nova_creds
import json
from environ import getenviromentvars
import optparse
import logging
import sys
from __version__ import version

creds = get_nova_creds()
nova = nvclient.Client(**creds)
def sever_list_clear():
	server_list = nova.servers.list()
	for server in server_list:
		print "prcessing:%s" % (server.id)
		if server.name[:8] == "whenenv-":
			print "deleting:%s" % (server.name)
			server.delete()
#sever_list_clear()

def shuttdown_by_id(catalogue,ident):
	#print ident
	#print catalogue[ident]
	server_list = nova.servers.list()
	for server in server_list:
		#print "prcessing:%s" % (server.id)
		if server.id == catalogue[ident]['OS_ID']:
			print "deleting:%s" % (server.name)
			server.delete()
			print "server.status:%s" % (server.status)
def read_input(filename):
	f = open(filename)
	json_string = f.read()
	loadedfile = json.loads(json_string)
	return loadedfile

def prototype(input_name):
	#print getenviromentvars()
	sever_list_clear()


def process_actions(input_name,output_name):
    env_set_termial = set(["TERMINAL_SSH_CONNECTION",
        "TERMINAL_XAUTHLOCALHOSTNAME",
        "TERMINAL_GPG_TTY"])
    env_set_jenkins = set(["JENKINS_BUILD_TAG",
        "JENKINS_BUILD_URL",
        "JENKINS_EXECUTOR_NUMBER",
        "JENKINS_NODE_NAME",
        "JENKINS_WORKSPACE"])
    
    env_var = getenviromentvars()
    terminal_use = False
    jenkins_use = False
    terminal_set = env_set_termial.intersection(env_var)
    jenkins_set = env_set_jenkins.intersection(env_var)
    if len(terminal_set) > 0:
        terminal_use = True
    if len(jenkins_set) > 0:
        jenkins_use = True

    matchset = set()
    if terminal_use:
        matchset = matchset.union(env_set_termial)
    if jenkins_use:
        matchset = matchset.union(env_set_jenkins)
    
    
    
    output_data = read_input(output_name)
    delete_set = set()
    for key in output_data:
        contnent = output_data[key].keys()
        keys_intersection = matchset.intersection(contnent)
        if len(keys_intersection) == 0:
            continue
        difference = False
        for intersect in keys_intersection:
            env_data = env_var[intersect]
            db_data = output_data[key][intersect]
            if (env_data == db_data):
                
                continue
            print intersect, env_data
            difference = True
        if not difference:
            delete_set.add(key)
    print delete_set
    for todel in delete_set:
        shuttdown_by_id(output_data,todel)
            

def main():
    
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logcfg', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-v', '--verbose', action ='count',help='Change global log level, increasing log output.', metavar='LOGFILE')
    p.add_option('-q', '--quiet', action ='count',help='Change global log level, decreasing log output.', metavar='LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Configuration file.', metavar='CFG_FILE')
    p.add_option('--input', action ='store',help='Called by udev $name')
    p.add_option('--output', action ='store',help='List all known instalations')
    p.add_option('--prototype', action ='store_true',help='List all known instalations')
    p.add_option('--bysession', action ='store_true',help='List all known instalations')
    input_file = None
    output_file = None
    actions = set()
    requires = set()
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
        output['pmpman.path.cfg'] = options.logcfg

    log = logging.getLogger("main")
    if options.prototype:
        actions.add("prototype")
    if options.bysession:
        actions.add("bysession")
    
    if options.input:
        input_file = options.input
        
    if options.output:
        output_file = options.output

    if options.database:
        output['pmpman.rdms'] = options.database
    
    if "prototype" in actions:
        prototype(input_file)
        sys.exit (0)
    if "bysession" in actions:
        process_actions(str(input_file),output_file)
    
    return 
if __name__ == "__main__":
    main() 
