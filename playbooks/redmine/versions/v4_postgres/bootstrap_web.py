from ipdb import set_trace
from liftoff.utils import remember_cwd
from fabric import Connection
import os

def create_connection(credentials):
    ssh_user = credentials["ssh_user"]
    hostname = credentials["hostname"]
    # Connect to the instance
    return Connection("%s@%s" % (ssh_user, hostname))

def run(resname, appliance, credentials):
    """ Bootstraps this instance for a given application. """
    conn = create_connection(credentials)
    setup_ansible(conn)
    upload_setup_files(conn)
    setup_nginx(conn)

def setup_ansible(resnam, appliance, conn):
    conn.sudo("apt-get update")
    conn.sudo("apt-get --yes install software-properties-common")
    conn.sudo("apt-add-repository --yes --update ppa:ansible/ansible")
    conn.sudo("apt-get --yes install ansible")

def upload_setup_files(conn):
    conn.run("rm -Rf files")
    conn.run("mkdir -p files")
    with remember_cwd():
        os.chdir("files")
        for f in os.listdir("."):
            if os.path.isfile(f):
                conn.put(f)
            else:
                tarball = "%s.tar.bz2" % f
                conn.local("tar -zcvf %s %s" % (tarball, f))
                conn.put(tarball, "files/")
                conn.local("rm %s" % tarball)
                conn.run("cd files && tar -zxvf %s" % tarball)
                conn.run("rm files/%s" % tarball)

def setup_nginx(conn):
    conn.run("ansible-galaxy install nginxinc.nginx")
    conn.run("ansible-playbook files/nginx/playbook.yml")
