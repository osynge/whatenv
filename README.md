# python-openstack-whenenv-integration #

These scripts are designed to buildup and tear down clusters of virtual
machines for the purposes of functional testing of cluster software such
as ceph with openstack as an IAS provider. They use a steering file to guide the
cluster creation, that supports user markup, generating a properties file to
allow cluster instalation to be started.

These scripts do not depend on whenenv. Whenenv does not directly have
the functionality to make cloud environments, but could easily work with some
buildup and tear down clusters of virtual machines for the purposes of
functional testing of cluster software such as ceph-especially when working with
rich matrix test jobs.

## Features ##

* Session concept to allow cleanup and prevent side effects.
* Simple steering file to building and marking up clusters.
* Rich cluster state file generation to allow cluster testing.
* Detects if session run from jenkins / terminal.
* Auto teardown of last session.
* "Debounces" until all VM initialized.
* Fixes IP address and hostnames ssh knownhosts.
* All scripts have built in help.
* Highly configurable logging verbosity.

## Usage ##

These scripts will evolve a little but thier current usage is shown.

Boot VM's from my steering file.

    osweint_buildup \
        --cfg $OS_CFG \
        --steering $STEERING_FILE \
        --state $CLUSTER_STATE

Block until all VM's are booted, and fix ssh keys to log in as root.

    osweint_debounce \
        --cfg $OS_CFG \
        --state $CLUSTER_STATE


To shutdown all VM's after tests have run:

	osweint_teardown \
        --cfg $OS_CFG \
        --session-del

Or alternatively if you wish to kill all VM's started by this script:

    osweint_teardown \
        --cfg $OS_CFG \
        --state $CLUSTER_STATE \
        --all

To list the VM's

    osweint_teardown \
        --cfg $OS_CFG \
        --instance-list

To list the sessions

    osweint_teardown \
        --cfg $OS_CFG \
        --session-list

## Instalation ##

For suse platforms you can install easily via rpm via OBS:

    https://build.opensuse.org/package/show/home:oms101:buildtools/python-openstack-whenenv-integration

The application requires an ssh key pair called:
        
    ${HOME}/.ssh/id_rsa
    ${HOME}/.ssh/id_rsa.pub

The application will add teh file public key file to the Open Stack user as mykey.

### Building from source ###

you can download the source from github:

    https://github.com/osynge/python-openstack-whenenv-integration

or yokel.org:

    http://www.yokel.org/pub/software/yokel.org/scientific/6/release/src/tgz/osweint-${VERSION}.src.tar.gz

To install the python script.

    $ cd $CODE_DIRECTORY
    $ python setup.py install

For further build options, including building rpms please look 

## FAQ ##

1. osweint_debounce fails asks for passwords and does not finish.

osweint_debounce tries to use ssh to log into to each host via Ipaddress 
and hostname. It will time out after 10 seconds attempting to contact each 
host so thiers no need to enter passwords.
This will occure under normal operation. 
If the behaviour is not normal, and passwords just keep coming up, you 
probably have a ssh-key setup issue.

2. I want more logging.

All these scritps have a rich logging system. Adding a '-v' paramter will
increase the default logging level. The '-q' paramter will do the oposite.
You can add '-q' and '-v' paramters as often as you like. For example:

    osweint_teardown \
        --cfg $OS_CFG \
        --session-list \
        -vvvv

Will run the command with a high level of logging.


## ROADMAP ##

These scripts are converting to an MVC pattern from a series of linear
scripts. Currently to much data uses the state file as the model. This
is being phased out in stages, and as much data as possible is being placed
in the MVC model. This will remove the need for $CLUSTER_STATE and generating
$CLUSTER_STATE will become optional. When this is complete the 3 separate cli
interfaces will be merged into one cli, having all the same functionality in 
a single cli.

These scripts will eventually be taken and absorbed into whenenv, to users of
whenenv no longer have to explictly call these scripts, and can simply markup
the job files with the desired environment they wish to run upon.

Better ssh key handling. so second user does not have to copy keys.

## About licensing ##

I hope that these scripts get absorbed by other projects, and only remain for
historical reference. i will happily change/relicense to suit integration,
in any open source projects that cannot work with the current license. I expect
contributors should feel the same.
