btsyncindicator
===============

Bittorrent Sync indicator for linux desktops

```
usage: btsyncindicator.py [-h] [--config CONFIG] [--iconpath ICONPATH]

optional arguments:
  -h, --help           show this help message and exit
  --config CONFIG      Location of Bittorrent Sync config file
  --iconpath ICONPATH  Path to icon theme folder
```

Displays an application indicator for Bittorrent Sync on Linux desktops.
Shows syncing folders and the status of connected peers.
Also allows you copy the secret for each folder to the clipboard.

## Installation

The recommended installation method is using the [Debian and Ubuntu Desktop Packages for BitTorrent Sync](http://forum.bittorrent.com/topic/19560-debian-and-ubuntu-desktop-packages-for-bittorrent-sync/) which includes the indicator.

### Ubuntu:
```
sudo add-apt-repository ppa:tuxpoldo/btsync
sudo apt-get update
sudo apt-get install btsync-user
```
The indicator will start on login with btsync

### Debian 
(i386 and amd64)
```
sudo gpg --keyserver pgp.mit.edu --recv-keys 6BF18B15
sudo gpg --armor --export 6BF18B15 | sudo apt-key add -

sudo echo deb http://debian.yeasoft.net/btsync $(lsb_release -cs) main contrib non-free >> /etc/apt/sources.list.d/btsync.list
sudo echo deb-src http://debian.yeasoft.net/btsync $(lsb_release -cs) main contrib non-free >> /etc/apt/sources.list.d/btsync.list

sudo apt-get update
sudo apt-get install btsync-user
```
The indicator will start on login with btsync

### Other Distros
```
cd ~/
git clone https://github.com/marxjohnson/btsyncindicator.git
```
Run `~/btsyncindicator/btsyncindicator`
You may want to add it to your startup applications to run on login

## Documentation

The API used by the indicator is (partially) documented on the [GitHub Wiki](https://github.com/marxjohnson/btsyncindicator/wiki)

Copyright Mark Johnson <mark@barrenfrozenwasteland.com> 2013
Released under GNU Lesser General Public License V3
