
import functools
import os
import boto3
from ipdb import set_trace
from pprint import pprint

from liftoff.utils import fullpath, ensure_pdir, ensure_object, remember_cwd
rds = boto3.client('rds')
ec2 = boto3.client('ec2')
ec2r = boto3.resource('ec2')

#####  Developer API
def get_instances(appliance):
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
        if instance.Tags.Product != appliance.name: continue
        if instance.Tags.Version != appliance.version: continue

        out.append(instance._values)
    return ensure_object(out)

#####  Product Deployer API
def create_key_pair(KeyName, KeyFile, force = False):
    """ Creates a key pair for a given product and stores it locally.  
    If it already exists 'force' option can be used to recreate it.
    """

    # Ensure parent folder exists since we are writing to it
    KeyFilePath = fullpath(KeyFile)
    ensure_pdir(KeyFilePath)

    keypairs = ec2.describe_key_pairs()['KeyPairs']
    if keypairs and any(d.get('KeyName', None) == KeyName for d in keypairs):
        # If it already exists then ensure key file path exists
        delkeypair = force
        if not os.path.isfile(KeyFilePath):
            if not force:
                assert False, "Key pair already exists but key file path is missing.  Use force = True"
        elif not force:
            # Already exists, do nothing and leave
            return 
        if delkeypair:
            if os.path.isfile(KeyFilePath):
                os.chmod(KeyFilePath, 0o777)
                os.remove(KeyFilePath)
            ec2.delete_key_pair(KeyName = KeyName, DryRun = False)

    # create key pair and output file
    key_pair = ec2.create_key_pair(KeyName=KeyName)
    KeyFile = open(KeyFilePath, "w")

    KeyPairOut = str(key_pair['KeyMaterial'])
    print(KeyPairOut)
    KeyFile.write(KeyPairOut)
    os.chmod(KeyFilePath, 0o400)
    return KeyPairOut

def ensure_security_groups(security_groups)
    """ Ensures that security groups with particular permissions exist. """
    curr_sec_groups = ec2.describe_security_groups()
    for newsg in security_groups:
        newsg = ensure_object(newsg)
        for sg in curr_sec_groups['SecurityGroups']:
            if sg['GroupName'] == newsg.GroupName:
                break
        else:
            sg = ec2.create_security_group(
                        GroupName = newsg.GroupName,
                        Description = newsg.Description)
            ec2.authorize_security_group_ingress(
                     GroupId = sg['GroupId'], 
                     IpPermissions = newsg.IpPermissions())

commands = {
    'create_key_pair': create_key_pair,
    'ensure_security_groups': ensure_security_groups,
    'create_instances': ec2r.create_instances
    'create_db_instance': rds.create_db_instance
}

def bootstrap_resource(resname, appliance, instance):
    """ Given a clean-slate instance, bootstraps the product by installing it and all its dependencies
    so this instance can be snapshotted into an AMI.
    """
    resconfig = appliance.resources[resname]

    with remember_cwd():
        os.chdir(os.path.dirname(appliance.config_path))
        contents = open(resconfig.bootstrap_script).read()
        pkgcode = compile(contents, resconfig.bootstrap_script, "exec")
        pkgdata = {}
        exec(pkgcode, pkgdata)
        runner = pkgdata['run']

        awsenv = resconfig.providers.aws
        # Connect to the instance
        from fabric import Connection
        conn = Connection("%s@%s" % (awsenv.ssh_user, instance.PublicDnsName))
        runner(resname, appliance, conn)
        return conn
