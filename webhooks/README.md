# SudoBot

## Installation

### OS Prerequisites

Install the following OS packages that will be required.

```
sudo apt install python3-venv uwsgi nginx
```

### Clone / Download

First you need to pull the code down and place within the directory that your webserver will serve it from.

```
git clone https://github.com/willdeberry/SudoBot.git
```

### VirtualEnv Setup

Make sure you have the virtualenv package installed and create the directory that the virtualenv will live in.
Go ahead and move to the directory where everything was cloned into and proceed with virtualenv creation.

```
cd SudoBot/webhooks
sudo apt install python3-venv
mkdir venv
python3 -m venv venv
```

Next, activate your new virtualenv and start installing packages.

```
source venv/bin/activate
python -m pip install -r requirements.txt
deactivate
```

### UWSGI

Now you need to configure uwsgi to point to your code and virtualenv in order for it to run the code on behalf of
nginx whenever it routes calls to it.

I created a file within `/etc/uwsgi/apps-available/sudobot.ini`:
```
[uwsgi]
module = main:app
master = true
plugins = python3
chdir = /var/www/sudobot
processes = 5
socket = sudobot.sock
chmod-socket = 660
vacuum = true
virtualenv = venv
die-on-term = true
touch-reload = /var/www/sudobot/main.py
```

Now you need to create a symlink from this ini file within the /etc/uwsgi/apps-enabled directory in order for UWSGI to
run it on service start.

```
cd /etc/uwsgi/apps-enabled
sudo ln -s ../apps-available/sudobot.ini
```

Now that's done, time to move onto nginx.

### Nginx

In order for this code to run, we have to point nginx to the uwsgi running socket.

Create a conf file for nginx with `/etc/nginx/conf.d/sudobot.conf`
```
server {
    listen 80;
    server_name <replace with server name>;

    root /var/www/sudobot;

    include /etc/nginx/snippets/headers.conf;

    location / {
        limit_except POST {
            deny all;
        }

        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name <replace with server name>;

    root /var/www/sudobot;

    include /etc/nginx/snippets/headers.conf;
    include /etc/nginx/snippets/ssl.conf;

    location / {
        limit_except POST {
            deny all;
        }

        include uwsgi_params;
        uwsgi_pass unix:/var/www/sudobot/sudobot.sock;
    }
}
```

### Startup

Now that all the configuration is in place, restart the services and hope it all just works.

```
sudo systemctl restart nginx.service uwsgi.service
```
