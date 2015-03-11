# python-openstack-whenenv-integration #

These scripts are designed to buildup and tear down clusters of virtual
machines for the purposes of functional testing of cluster software such
as ceph with openstack as an IAS provider. They use a steering file to guide the
cluster creation, that supports user markup, generating a properties file to
allow cluster instalation to be started.

These scripts do not depend on whenenv.

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

### SUSE instalation ###

For suse platforms you can install easily via rpm via OBS:

    https://build.opensuse.org/package/show/home:oms101:buildtools/python-openstack-whenenv-integration

### Building from source ###

you can download the source from github:

    https://github.com/osynge/python-openstack-whenenv-integration

or yokel.org:

    http://www.yokel.org/pub/software/yokel.org/scientific/6/release/src/tgz/osweint-${VERSION}.src.tar.gz

To install the python script.

    $ cd $CODE_DIRECTORY
    $ python setup.py install

For further build options, including building rpms please look

## Setup ##


### Setup : ssh keys ###

The application requires an ssh key pair called:

    ${HOME}/.ssh/id_rsa
    ${HOME}/.ssh/id_rsa.pub

The application will add the file public key file to the Open Stack user as mykey.

### Setup : SSUE Cloud account ##

Create a config file with your account details wtih the name "susecloud.cfg"

    [main]
    username="my user name"
    password="my password"
    auth_url="https://example.org:5000/v2.0/"
    tenant="my tennant / project"

The auth_url can be set to the 1.1, 2, or 3 api for the cloud.

### Setup : Sterring file. ###

Example Steering file.

    {
        "label" : {
            "a1de224d-a5af-4cbf-9ca1-74e23f838078" :{
                    "CEPH_LAYOUT" : ["OSD","MON"]
                },
            "1dcf1312-1aee-42b2-8467-c169d84953a1" :{
                    "CEPH_LAYOUT" : ["OSD"]
                },
            "2f24a10e-47ef-46d8-91aa-3f51536e8795" :{
                    "CEPH_LAYOUT" : ["MON"]
                },
            "95d5743f-0202-4508-926b-45a5c34ca151" :{
                    "CEPH_LAYOUT" : ["CDEPLOY"]
                },
            "6099d367-c871-4b9f-a938-272a18cd843e" :{
                    "OS_INSTALLED" : ["SLE_12"]
                },
            "9c2810e7-7473-4581-a31f-9b8bca33f820" :{
                    "OSD_DISK" : ["vdb"]
                }

        },
        "images": {
            "4c78fed1-9986-43a0-8215-297438671214":
                {
                    "OS_IMAGE_NAME": "SLES12",
                    "usr_label" : ["6099d367-c871-4b9f-a938-272a18cd843e"]
                }
            },
        "flavor": {
            "eba0b488-00ad-4046-9990-648ebdf8f56e" :
                {
                    "OS_FLAVOR_NAME" : "d2.tiny",
                    "usr_label" : ["9c2810e7-7473-4581-a31f-9b8bca33f820"]
                }
            },
        "instances" : { "bb4089cf-b2fc-4332-9217-4d4add6a0391" : {
                "uuid_image" : "4c78fed1-9986-43a0-8215-297438671214",
                "uuid_flavour" : "eba0b488-00ad-4046-9990-648ebdf8f56e",
                "usr_label" : ["a1de224d-a5af-4cbf-9ca1-74e23f838078"]
            },
            "77fe8791-dbc1-46cd-a42c-91b0f978699b": {
                "uuid_image" : "4c78fed1-9986-43a0-8215-297438671214",
                "uuid_flavour" : "eba0b488-00ad-4046-9990-648ebdf8f56e",
                "usr_label" : ["a1de224d-a5af-4cbf-9ca1-74e23f838078"]
            },
            "8afc7048-92e1-4618-9a83-a60071d68525" : {
                "uuid_image" : "4c78fed1-9986-43a0-8215-297438671214",
                "uuid_flavour" : "eba0b488-00ad-4046-9990-648ebdf8f56e",
                "usr_label" : ["1dcf1312-1aee-42b2-8467-c169d84953a1"]
            },
            "05dac44d-cea0-4456-bef7-153e1cd74d44" : {
                "uuid_image" : "4c78fed1-9986-43a0-8215-297438671214",
                "uuid_flavour" : "eba0b488-00ad-4046-9990-648ebdf8f56e",
                "usr_label" : ["2f24a10e-47ef-46d8-91aa-3f51536e8795"]
            },
            "24f140b8-8446-46c2-9d80-58614dcfb5e4" : {
                "uuid_image" : "4c78fed1-9986-43a0-8215-297438671214",
                "uuid_flavour" : "eba0b488-00ad-4046-9990-648ebdf8f56e",
                "usr_label" : ["95d5743f-0202-4508-926b-45a5c34ca151"]
            }
        }
    }


### Setup : Sterring file : images ###

Images are a JSON dict. The key is an identifier and string of your
choice and only must be unique within the steering file(s) used in a
session. The value is a dictionary also.

The image instances value is used to query SUSE cloud / Open Stack for
images to initialise into Virtual Hosts using the special key
"OS_IMAGE_NAME". "usr_label" lists can also be added.







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

Come up with a better name and rename the project. Current best name is 
"whatenv" as it makes the environment you want in the cloud. Suggestions 
great-fully accepted.

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
