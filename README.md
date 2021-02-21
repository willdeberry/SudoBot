# SudoBot

## Summary

Installation will be focused on running this bot on Ubuntu.

## Installation

### OS Prerequisites

You will need to use `apt` to install the following packages.

```
sudo apt install python3-requests python3-systemd python3-dotenv
```

### Pip Prerequisites

This is the only python package that isn't available via the OS's package manager. So we will have to rely on `pip3` to
install for us.

```
pip3 install discord
```

### Clone / Download

Next you will want to pull this bot down and install on the system. Keep in mind that it doesn't matter where you clone
it to, just be aware of the path since we will use this later when setting up the systemd unit file.

```
git clone https://github.com/willdeberry/SudoBot.git
```

## Running

Now that the bot is on the server, we need to tell the OS to run the code. This is where `systemd` comes in.

I placed this unit file where systemd can find it: `/etc/systemd/system/sudobot.service`

```
[Unit]
Requires=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/sudobot

[Install]
WantedBy=multi-user.target
```

Replace the path in `ExecStart` with the path to `sudobot.py`. This will be different for all depending on where you
performed the clone.

Next, we need to tell `systemd` that we created a new unit file.

```
sudo systemctl daemon-reload
```

Now we should be able to start it up.

```
sudo systemctl start sudobot.service
```

Then you can ask `systemd` the status of the unit file to make sure it startup cleanly.

```
jsmith@ubuntu:/$ sudo systemctl status sudobot.service
● sudobot.service
     Loaded: loaded (/etc/systemd/system/sudobot.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2021-02-21 02:46:06 UTC; 41min ago
   Main PID: 110858 (python3)
      Tasks: 3 (limit: 1160)
     Memory: 30.1M
     CGroup: /system.slice/sudobot.service
             └─110858 python3 /usr/bin/sudobot
```
