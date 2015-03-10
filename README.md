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
* "Debounces" until all VM initialised.
* Fixes IP address and hostnames ssh knownhosts.

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
        --state  $CLUSTER_STATE \
        --bysession

Or alternatively if you wish t kill all VM's started by this script:

    osweint_teardown \
        --cfg $OS_CFG \
        --state  $CLUSTER_STATE \
        --all


## ROADMAP ##

These scripts are converting to an MVC pattern from a series of linear
scripts. Currently to much data uses the state file as the model. This
is being phased out in stages, and asmuch data as possible is being placed
in the MVC model. This will remove the need for $CLUSTER_STATE and generating
$CLUSTER_STATE will become optional.

These scripts will eventually be taken and absorbed into whenenv, to users of
whenenv no longer have to explictly call these scripts, and can simply markup
the job files with the desired environment they wish to run upon.

## About licensing ##

I hope that these scripts get absorbed by other projects, and only remain for
historical reference. i will happily change/relicense to suit integration,
in any open source projects that cannot work with the current license. I expect
contributors should feel the same.
