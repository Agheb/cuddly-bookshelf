# Linux Server Configuration Project 

This is the last project for "Full Stack Web Developer Nanodegree" on Udacity.
In this project, we will dockerize a simple Python Flask App and deploy it on AWS Lightsail.  
Public IP: 52.57.9.218  
URL: www.amanuelg.me  
Port: 2200  

# Part 1: Server Configuration

Launch a  LightSail instance with Ubuntu and connect to it using SSH. You need to download the default private key from the LightSail website. Don't forget to set the proper permissions for that file.

## Update your ubuntu instance
```bash
$ sudo apt-get update
$ sudo apt-get upgrade
```
## Install Docker
[How To Install and Use Docker on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04)

## Install Docker-Compose
[How To Install Docker Compose on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04)

## Create a new user and grant sudo privileges 
```
$ sudo adduser grader
$ sudo visudo
```
In your Visudo File look for this line:
```
root    ALL=(ALL:ALL) ALL
```
Then add this line to grant user grader sudo privileges:
```
grader  ALL=(ALL:ALL) ALL
```
## Set SSH login using keys
```
$ mkdir .ssh
$ sudo touch .ssh/authorized_keys
```
Copy public key into this file, save it and set proper permissions:
```
$ sudo nano .ssh/authorized_keys
$ chmod 700 .ssh
$ chmod 644 .ssh/authorized_keys
```
## Set SSH Port to non default port 2200
1. Add Port 2200 through Lightsail web interface
2. Open sshd config file: `sudo nano /etc/ssh/sshd_config`
3. Change `Port:20` to `Port:2200`
4. Change `PermitRootLogin prohibit-password` to `PermitRootLogin no`
5. Save changes and then restart sshd service `sudo /etc/init.d/ssh restart`

## Configure the local timezone to UTC
1. Configure the time zone `sudo dpkg-reconfigure tzdata`
2. Set it to `UTC`

## Configuring Firewall
Configure firewall rules using UFW. Check to see if ufw is active: `sudo ufw status`. If not active, lets add some rules
```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2200/tcp
sudo ufw allow 80/tcp or sudo ufw allow www (either one of these commands will work)
sudo ufw allow 123/udp
```
Now, enable the rules: `sudo ufw enable`


# Part 2: Dockerize Bookshelf App 
To suit my needs, i made the extra effort to learn the ins and outs of Docker.
For this task, we will spin up two containers: one named `web` to run our python app with `uWSGI` and `Nginx`. The other named `postgres` to run a `PostgresSQL` database server. 

## Prepare Bookshelf Flask App for Production;
1. Replace/Copy app content in folder `app`
2. In `__init__.py` change the config object to `postgres`
3. In `config.py` set database name, user, password and URLs
```python
POSTGRES_USER = 'foo'
POSTGRES_PASSWORD = 'foobar'
POSTGRES_DB = 'prod'
UPLOADS_DEFAULT_URL = '<YOUR_URL>/static/img/'
UPLOADED_IMAGES_URL = '<YOUR_URL>/static/img/'
```
## Container 'Web'
1. Build our own Docker Image via a Dockerfile
```Dockerfile
FROM tiangolo/uwsgi-nginx:python2.7 

MAINTAINER Amanuel Ghebreweldi

RUN pip install --upgrade pip

# Install all necessary Python dependencies
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --requirement /app/requirements.txt

# This is needed for PostgreSQL
RUN pip install psycopg2

# Copy Nginx config 
COPY nginx.conf /etc/nginx/conf.d/

# Copy Python app content 
COPY ./app /app
```
2. Create Nginx Config file called `nginx-conf`
```Nginx
server {
    location / {
        try_files $uri @app;
    }
    location @app {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }
    location /static {
        alias /app/bookshelf/static; ## serve static files from app
    }
}
```

Keep in mind to follow the same folder structure like the repo
## Define and run multiple containers with Docker-Compose
1. Create a `docker-compose.yml` file 
```YAML
version: '2'
services:
  web:
    container_name: 'web'
    # point to Dockerfile to build an image and use it afterwards
    build: .  
    ports:
    # map ports from HOST:CONTAINER
      - "80:80"
    volumes:
    - ./app:/app
    # link to other container postgres and its service
    depends_on:
      - postgres

  postgres:
    container_name: 'postgres'
    image: postgres:latest
    environment:
      # set the same ENV variables specified in config.py
      POSTGRES_USER : foo
      POSTGRES_PASSWORD : foobar
      POSTGRES_DB : prod
    volumes:
      - pgdata:/var/lib/postgresql/data/
    ports:
      - "5432:5432"

volumes:
  pgdata:
```
2. Clone your repo into your AWS Lightsail instance
3. Go to your repo directory and build your image:
```bash
$ docker-compose build
```
4. Run your Docker Containers
```bash
$ docker-compose up`
``` 
5. Init Database with some sample data
```bash
$ docker-compose run web /usr/local/bin/python /app/db_setup.py
```

# Issues encountered
 * Bookshelf is using Google for login authentification. Public IPs are not allowed to handle responses from Google's authorization server. You need a public top-level domain. Luckily if you are a student, you can get one for free at [Namescheap](https://nc.me/)

# Resources
 * [Server Setup with Ubuntu](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04)
 * [AWS Lightsail Documenation](https://aws.amazon.com/documentation/lightsail/)
 * [How to use Docker and Docker Compose to Create a Flask Application](http://www.patricksoftwareblog.com/how-to-use-docker-and-docker-compose-to-create-a-flask-application/)
 * [Why You Should Stop Installing Your WebDev Environment Locally](https://www.smashingmagazine.com/2016/04/stop-installing-your-webdev-environment-locally-with-docker/)


