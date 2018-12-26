from fabric import task

@task
def bootstrap(conn):
    conn.sudo("apt-get --yes update")
    conn.sudo("apt-get --yes install build-essential python2.7")
    conn.sudo("apt-get --yes install python-pip")
