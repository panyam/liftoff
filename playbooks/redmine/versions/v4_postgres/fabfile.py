from fabric import task

@task
def bootstrap(conn):
    conn.sudo("apt-get --yes update")
    conn.sudo("apt-get --yes install build-essential")
    conn.sudo("apt-get --yes install python2.7")
    conn.sudo("apt-get --yes install python-pip")

@task
def setup_redmine(conn):
    conn.sudo("apt-get install libopenssl-ruby1.8")
    conn.sudo("gem install nokogiri v'1.8.5'")
    with cd("/home/ubuntu/redmine-4.0.0"):
        conn.run("bundle install --without development test rmagick")
        conn.run("bundle exec rake generate_secret_token")
        conn.run("RAILS_ENV=production bundle exec rake db:migrate")
        conn.run("RAILS_ENV=production REDMINE_LANG=en bundle exec rake redmine:load_default_data")
    conn.run("date >> /home/ubuntu/redmine-4.0.0/install_timestamp")
