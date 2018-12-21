from ipdb import set_trace
from liftoff.utils import remember_cwd
import os

def run(resname, appliance, conn):
    """ Bootstraps this instance for a given application. """
    # setup_ansible(conn)
    # upload_setup_files(resname, appliance, conn)
    setup_nginx(resname, appliance, conn)

def setup_ansible(resnam, appliance, conn):
    conn.sudo("apt-get update")
    conn.sudo("apt-get --yes install software-properties-common")
    conn.sudo("apt-add-repository --yes --update ppa:ansible/ansible")
    conn.sudo("apt-get --yes install ansible")

def upload_setup_files(resname, appliance, conn):
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

def setup_nginx(resname, appliance, conn):
    conn.run("ansible-galaxy install nginxinc.nginx")
    conn.run("ansible-playbook files/nginx/playbook.yml")
