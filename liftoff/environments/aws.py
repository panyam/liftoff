
import functools
import os
import boto3
from ipdb import set_trace
from pprint import pprint

from liftoff.utils import fullpath, ensure_pdir, ensure_object
ec2 = boto3.client('ec2')
ec2r = boto3.resource('ec2')

# What are the goals of our "installer".
# We have two kinds of users - creators of products and users of products.
# 
#   1. For creators of products - we want to setup different kind of "setups", eg:
#       a. N db resources
#       b. M app resources
#       c. X type Y resources and so on.
#       d. Optionally for each resource group have some kind of DNS/logical name/LB support for it
#
#   2. For users of the product, we just want this to be "deployed" and used per the u
#       resource spec as specified.  This would result in:
#       a. The resource groups as specified by dev.
#       b. A way to access this service (either internally or externally)

#####  Developer API
def get_instances(configs):
    # Get all instances running this product
    reservations = ec2.describe_instances()['Reservations']
    instances = functools.reduce(lambda x,y:x + y, [r['Instances'] for r in reservations], [])
    out = []
    for instance in instances:
        # Check state
        instance = ensure_object(instance)
        if instance.State.Name == "terminated": continue
    
        # Check tags
        instance['Tags'] = dict([(tag['Key'],tag['Value']) for tag in instance.Tags])
        if instance.Tags.Product != configs.product.name: continue
        if instance.Tags.Version != configs.product.version: continue

        out.append(instance._values)
    return ensure_object(out)

def create_raw_instance(configs, dry_run = True):
    """ Create a clean-slate/raw instance on which the product and all its dependancies will 
    be deployed before it can be snapshotted for easy installation/launching.
    """
    awsenv = configs.env.aws
    key_pair = create_key_pair(configs, False)
    instance = ec2r.create_instances(
                ImageId = awsenv.ami,
                InstanceType = awsenv.instance_type,
                MinCount = 1, MaxCount = 1,
                KeyName = awsenv.key_name,
                DryRun = dry_run,
                SecurityGroups = [awsenv.security_group.name],
                TagSpecifications = [
                    {
                        'ResourceType': 'instance', 
                        'Tags': [
                            { 'Key': 'Product', 'Value': configs.product.name },
                            { 'Key': 'Version', 'Value': configs.product.version },
                        ]
                    }
                ])
    return instance

def bootstram_instance(configs, instance):
    """ Given a clean-slate instance, bootstraps the product by installing it and all its dependencies
    so this instance can be snapshotted into an AMI.
    """
    pass

def make_snapshot(configs, instance):
    """ After a bootstrap is complete, the instance is snapshotted for easy installation. """
    pass

#####  Product Deployer API
def launch_product(product):
    """ Launches the product by bringing up the required instances as described by the product's manifest. """
    pass

def ssh(instanceid):
    pass

def create_key_pair(configs, force = False):
    """ Creates a key pair for a given product and stores it locally.  
    If it already exists 'force' option can be used to recreate it.
    """

    # Ensure parent folder exists since we are writing to it
    awsenv = configs.env.aws
    key_name = awsenv.key_name
    key_file_path = fullpath(awsenv.key_file)
    ensure_pdir(key_file_path)

    keypairs = ec2.describe_key_pairs()['KeyPairs']
    if keypairs and any(d.get('KeyName', None) == key_name for d in keypairs):
        # If it already exists then ensure key file path exists
        delkeypair = force
        if not os.path.isfile(key_file_path):
            if not force:
                assert False, "Key pair already exists but key file path is missing.  Use force = True"
        elif not force:
            # Already exists, do nothing and leave
            return 
        if delkeypair:
            if os.path.isfile(key_file_path):
                os.chmod(key_file_path, 0o777)
                os.remove(key_file_path)
            ec2.delete_key_pair(KeyName = key_name, DryRun = False)

    # create key pair and output file
    key_pair = ec2.create_key_pair(KeyName=key_name)
    key_file = open(key_file_path, "w")

    KeyPairOut = str(key_pair['KeyMaterial'])
    print(KeyPairOut)
    key_file.write(KeyPairOut)
    os.chmod(key_file_path, 0o400)
    return KeyPairOut

def ensure_security_group(configs):
    awsenv = configs.env.aws
    sgs = ec2.describe_security_groups()
    for sg in sgs['SecurityGroups']:
        if sg['GroupName'] == awsenv.security_group.name:
            return sg
    sg = ec2.create_security_group(
                GroupName = awsenv.security_group.name,
                Description = "Default security group for launching VMs.")

    ec2.authorize_security_group_ingress(
             GroupId = sg['GroupId'], 
             IpPermissions = [
                 {
                    'FromPort': 22, 'IpProtocol': 'tcp',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'Ipv6Ranges': [],
                    'PrefixListIds': [],
                    'ToPort': 22,
                    'UserIdGroupPairs': []
                },
                {
                    'FromPort': 80, 'IpProtocol': 'tcp',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'Ipv6Ranges': [],
                    'PrefixListIds': [],
                    'ToPort': 80,
                    'UserIdGroupPairs': []
                },
                {
                    'FromPort': 443, 'IpProtocol': 'tcp',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'Ipv6Ranges': [],
                    'PrefixListIds': [],
                    'ToPort': 443,
                    'UserIdGroupPairs': []
                },
                {
                    'FromPort': 0, 'IpProtocol': 'icmp',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'Ipv6Ranges': [],
                    'PrefixListIds': [],
                    'ToPort': 0,
                    'UserIdGroupPairs': []
                }
            ])

