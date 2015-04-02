# whatenv #

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

    whatenv_buildup \
        --cfg $OS_CFG \
        --steering $STEERING_FILE \
        --state $CLUSTER_STATE

Block until all VM's are booted, and fix ssh keys to log in as root.

    whatenv_debounce \
        --cfg $OS_CFG \
        --state $CLUSTER_STATE


To shutdown all VM's after tests have run:

	whatenv_teardown \
        --cfg $OS_CFG \
        --session-del

Or alternatively if you wish to kill all VM's started by this script:

    whatenv_teardown \
        --cfg $OS_CFG \
        --all

To list the VM's

    whatenv_teardown \
        --cfg $OS_CFG \
        --instance-list

To list the sessions

    whatenv_teardown \
        --cfg $OS_CFG \
        --session-list

## Instalation ##

### SUSE instalation ###

For suse platforms you can install easily via rpm via OBS:

    https://build.opensuse.org/package/show/home:oms101:buildtools/python-whatenv

### Building from source ###

you can download the source from github:

    https://github.com/osynge/whatenv

or yokel.org:

    http://www.yokel.org/pub/software/yokel.org/scientific/6/release/src/tgz/whatenv-${VERSION}.src.tar.gz

To install the python script.

    $ cd $CODE_DIRECTORY
    $ python setup.py install

For further build options, including building rpms please look

## Setup ##


### Setup : ssh keys ###

The application requires a password less ssh key pair called:

    ${HOME}/.ssh/id_rsa
    ${HOME}/.ssh/id_rsa.pub

The application will add the file public key file to the Open Stack user as mykey.

### Setup : SUSE Cloud account ##

Create a config file with your account details with the name "susecloud.cfg"

    [main]
    username="my user name"
    password="my password"
    auth_url="https://example.org:5000/v2.0/"
    tenant="my tennant / project"

The auth_url can be set to the 1.1, 2, or 3 api for the cloud.

### Setup : Steering file. ###

The steering file is the most important configuration file for whatenv.
This defines what virtual machine instances will be created and destroyed
as part of a session.

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

### Setup : Steering file : Introduction ###

The steering file is a json dictionary, with 4 keys.

* label
* images
* flavor
* instances

Each of these 4 keys have a value of a dictionary. These dictionaries have
identifiers. These identifiers can have any value and have no significance
outside this file and are just surrogate keys to associated the 4 types of
metadata presented by whatenv to the open stack cloud. In the above example
these identifiers are uuid's but they could equally well be more descriptive
such as label_01, image_04, flavor_32, instance_controller.


### Setup : Steering file : instances ###

Your test cluster is a made up of a collection of instances, these instances
are the VM hosts you want to be created and destroyed on each testing cycle.

Each VM may be different from other VM's or similar. These VM's will all need
to be destroyed at the end of each testing cycle as well as created in each
testing cycle.

Within the instances dictionary we have a set of instance dictionaries, each
identified by a unique identifier. This will be used to uniquely identify
which VM instance in the output state file. One instance corresponds to one VM
that will be instantiated.

Each instance needs to have a "uuid_image" to defied its operating system
image and one "uuid_flavour" to define it's hardware layout. Please see the
next sections to explain this in more detail.

Although instances can be be identified via the identifier, this causes
infelxabilities in interpreting the "state" file and combining and modifying
your test clusters. For this reason each instance can have a set of labels.
Please see the label section to explain this in more detail.


### Setup : Steering file : images ###

The open Stack instance you are accessing will have a series of VM images
available in the image store so you can run the appropriate Operating system
and version of that operating system. Whatenv must be able to select the
appropriate image to create VM instance for your use.

Within the images dictionary we have a set of images, each identified by a
unique identifier. This will be used by instances to specify which image is
used to create the instance.

Each image is also a JSON dictionary. The value is a dictionary and the value
must contain an "OS_IMAGE_NAME" key. as show above. This is used to select
the appropriate image, and must match an image name provided by SUSE cloud /
Open Stack.

Images like flavors and instances can reference a set of labels. These are
given the key "usr_label" and presented as a JSON list. labels are optional,
but recommended to allow easy use of your cluster.


### Setup : Steering file : flavor ###

The open Stack instance you are accessing will have a series of VM flavors
available, these define the disks, memory, and number of virtual CPU's.

Whatenv must be able to select the appropriate flavor to create VM instances
for your use.


Within the images dictionary we have a set of images, each identified by a
unique identifier. This will be used by instances to specify which image is
used to create the instance.

Each image is also a JSON dictionary. The value is a dictionary and the value
must contain an "OS_FLAVOR_NAME" key. as show above. This is used to select
the appropriate flavor, and must match an image name provided by SUSE cloud /
Open Stack.

Flavor like images and instances can reference a set of labels. These are
given the key "usr_label" and presented as a JSON list. labels are optional,
but recommended to allow easy use of your cluster.




### Setup : Steering file : labels ###

Labels are a JSON dictionaries. These JOSN dictionaries add metadata to the state
file. The final output is a merge of the metadata provided in the steering
file and an example is shown:

    "WE_USER_LABEL": {
        "CEPH_LAYOUT": [
                "OSD",
                "MON"
            ],
            "OSD_DISK": [
                "vdb"
            ],
            "OS_INSTALLED": [
                "SLE_12"
            ]

Labels can be attached to images, flavors or instances.

Since instances are composed of images and flavours in open stack, and
instances, images and flavours can all have labels, when an instance is
created by whatenv all the labales are added toether.

### Setup : Steering file : labels : Presidence ###

Should labels clash the one label must overide the previous label.
Labels are added in the order of presidence:

1. Instance
2. Image
3. Flavor

## FAQ ##

* whatenv_debounce fails asks for passwords and does not finish.

whatenv_debounce tries to use ssh to log into to each host via Ip address
and hostname. It will time out after 10 seconds attempting to contact each
host so theirs no need to enter passwords.
This will occur under normal operation.
If the behavior is not normal, and passwords just keep coming up, you
probably have a ssh-key setup issue.

* I want more logging.

All these scripts have a rich logging system. Adding a '-v' parameter will
increase the default logging level. The '-q' parameter will do the opposite.
You can add '-q' and '-v' parameters as often as you like. For example:

    whatenv_teardown \
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

Better ssh key handling. So second user with the same account does not have
to copy keys to each account.

## About licensing ##

I hope that these scripts get absorbed by other projects, and only remain for
historical reference. i will happily change/relicense to suit integration,
in any open source projects that cannot work with the current license. I expect
contributors should feel the same.

## Similar projects ##

### Puppet Labs Beaker ###

Puppet Labs cloud enabled acceptance testing tool. This project is the most
similar to whatenv but is very coupled to puppet.

    https://github.com/puppetlabs/beaker

### Docker's Compose ###

Compose is very similar for docker containers to whatenv for SUSEcloud /
openstack. Focused on orchestration and less on testing via jenkins.

    http://blog.docker.com/2015/02/orchestrating-docker-with-machine-swarm-and-compose/

### Open Stack's HEAT ###

This locks very interesting but was not practical for my use case at the time
of writing. Focused on orchestration and less on testing via jenkins.

    https://wiki.openstack.org/wiki/Heat

### Googles's kubernetes ###

This project is very interesting for the google PAS, and is very alpha
for IAS. It looks interesting and is part of the inspiration for labels
in the steering files. Focused on orchestration and less on testing
via jenkins.

    https://github.com/googlecloudplatform/kubernetes

### Quattor AII ###

Similar to whatenv but uses Open nebula RPC instructions to create VM's and
is integrated with Quattor to deploy the VM's software.

    https://github.com/quattor/aii/tree/master/aii-opennebula
