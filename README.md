btsyncindicator
===============

**BitTorrent Sync indicator for Linux desktops**

```
usage: btsyncindicator.py [-h] [--config CONFIG] [--iconpath ICONPATH]

optional arguments:
  -h, --help           show this help message and exit
  --config CONFIG      location of BitTorrent Sync config file
  --iconpath ICONPATH  path to icon theme folder
```

* Displays an application indicator for BitTorrent Sync on Linux desktops.
* Shows syncing folders and the status of connected peers.
* Allows you copy the secret for each folder to the clipboard.

## Installation

The recommended installation method is using the [Debian and Ubuntu Desktop Packages for BitTorrent Sync](http://forum.bittorrent.com/topic/19560-debian-and-ubuntu-desktop-packages-for-bittorrent-sync/) which includes the indicator.

### Ubuntu/Debian (i386, amd64, armel, and armhf)
```
sudo add-apt-repository ppa:tuxpoldo/btsync
sudo apt-get update
sudo apt-get install btsync-user
```
The indicator will start on login with BitTorrent Sync.

If you get a *command not found* error, run `sudo apt-get install python-software-properties python-software-common` first.

### Arch Linux
btsyncindicator is available in the [AUR](https://aur.archlinux.org).
```
sudo packer -S --noedit --noconfirm btsyncindicator
```

### Other distributions
The indicator is not packaged for other distros. You will have to [download BitTorrent Sync](http://labs.bittorrent.com/experiments/sync.html), then download and run the indicator seperately:
```
cd ~/
git clone https://github.com/marxjohnson/btsyncindicator.git
~/btsyncindicator/btsyncindicator.py`
```
You may want to make it start on login.

## Documentation

The API used by the indicator is (partially) documented on the [GitHub Wiki](https://github.com/marxjohnson/btsyncindicator/wiki)

Copyright Mark Johnson <mark@barrenfrozenwasteland.com> and contributors, 2013
Released under GNU Lesser General Public License V3
