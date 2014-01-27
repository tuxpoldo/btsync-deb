btsyncindicator
===============

**BitTorrent Sync indicator for Linux desktops**

```
usage: btsyncindicator.py [-h] [--config CONFIG] [--iconpath ICONPATH] [-v]
                          [--log LOG]

optional arguments:
  -h, --help           show this help message and exit
  --config CONFIG      Location of BitTorrent Sync config file
  --iconpath ICONPATH  Path to icon theme folder
  -v, --version        Print version information and exit
  --log LOG            Set logging level
```

* Displays an application indicator for BitTorrent Sync on Linux desktops.
* Shows syncing folders and the status of connected peers.
* Allows you copy the secret for each folder to the clipboard.

### Contributions welcome

I'm not actively developing the indicator at the moment but am keeping an eye on bug reports and will test and merge pull requests.  If you'd like to contribute, please raise a bug in the tracker, I'll be notified and get back to you.

## Installation

The recommended installation method is using the [Debian and Ubuntu Desktop Packages for BitTorrent Sync](http://forum.bittorrent.com/topic/19560-debian-and-ubuntu-desktop-packages-for-bittorrent-sync/) which includes the indicator.

### Ubuntu/Debian (i386, and amd64)
```
sudo add-apt-repository ppa:tuxpoldo/btsync
sudo apt-get update
sudo apt-get install btsync-user
```
If you get a *command not found* error, run `sudo apt-get install python-software-properties software-properties-common` first. 

The indicator will start on login with BitTorrent Sync.

### Debian (i386, amd64, powerpc, armel, and armhf)
```
sudo gpg --keyserver pgp.mit.edu --recv-keys 6BF18B15
sudo gpg --armor --export 6BF18B15 | sudo apt-key add -
sudo echo deb http://debian.yeasoft.net/btsync $(lsb_release -cs) main contrib non-free >> /etc/apt/sources.list.d/btsync.list
sudo echo deb-src http://debian.yeasoft.net/btsync $(lsb_release -cs) main contrib non-free >> /etc/apt/sources.list.d/btsync.list
sudo apt-get update
sudo apt-get install btsync-user
```
The indicator will start on login with BitTorrent Sync.

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
