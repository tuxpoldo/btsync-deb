# BitTorrent Sync Packaging Project

[![Build Status](https://img.shields.io/teamcity/https/teamcity.silvenga.com/e/Btsync_Build.svg?label=TeamCity&style=flat-square)](https://teamcity.silvenga.com/viewType.html?buildTypeId=Btsync_Build&guest=1)

I will be providing continued maintenance for this awesome project that Mr. Tuxpoldo has founded. Until I am accustomed to this project (or Python for the matter) I can provide support for the `btsync` and `btsync-common` packages with new binary versions and bugfixes.

Debian and Ubuntu packages can be found under my private repository http://deb.silvenga.com. New versions should be automatically built and published to this location via my build server (found above) when new changelogs are released. 

Cheers!

\- Silvenga

## Installing

Add my package signing key:

```
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 992A3C9A3C3DE741
```

Add the btsync repository:

```
add-apt-repository "deb http://deb.silvenga.com/btsync any main"
apt-get update
```

Install `btsync`

```
apt-get install btsync
```

After following the prompts, open your browser to `http://127.0.0.1:8888/gui/` (if using the default configuration).

## FAQ

### Issue

Adding a new synced folder results in the following error:

> Sync does not have permission to access this folder

### Solution

Make sure the user Btsync is running as has read and write access to the path set when prompted for the "Start path for the web interface". 

Alternatively, `/` can be used. 

### Issue

You would receive something like the following when running `apt-get-repository`:

```
Traceback (most recent call last):
  File "/usr/bin/add-apt-repository", line 167, in <module>
    sp = SoftwareProperties(options=options)
  File "/usr/lib/python3/dist-packages/softwareproperties/SoftwareProperties.py", line 105, in __init__
    self.reload_sourceslist()
  File "/usr/lib/python3/dist-packages/softwareproperties/SoftwareProperties.py", line 595, in reload_sourceslist
    self.distro.get_sources(self.sourceslist)
  File "/usr/lib/python3/dist-packages/aptsources/distro.py", line 89, in get_sources
    (self.id, self.codename))
aptsources.distro.NoDistroTemplateException: Error: could not find a distribution template for Raspbian/jessie
```

### Solution

Raspbian's `add-apt-repository` seems to be broken under at last Jessie. The following commands will resolve the issues:

```
echo "deb http://deb.silvenga.com/btsync any main" > /etc/apt/sources.list.d/silvenga-btsync-deb.list
apt-get update
apt-get install btsync
```

### Issue

Adding signing key fails with the following stacktrace:

```
gpg: requesting key 3C3DE741 from hkp server keyserver.ubuntu.com
gpg: no writable keyring found: eof
gpg: error reading `[stream]': general error
```

### Solution

Make sure to run all the above commands as `root` either by using `sudo` or switching to the `root` user. 

## TODO

* Log to proper log folder.
* Setup logrotate. 

## Original README

[BitTorrent&reg; Sync][1] from BitTorrent&reg; Inc. is a simple tool that
applies p2p protocol for direct live folder sync with maximum security, network
speed and storage capacity. It has native versions for Mac, Windows and Linux,
as well as native NAS integration.

BitTorrent&reg; Inc. __delivers for Linux users only a raw binary file without
any deployment concept or setup system__. It's up to the user to create a
reliable startup and shutdown logic and to manage a configuration file. Also a
dedicated GUI, as provided for Windows and Mac OSX is missing.

The scope of this project is to provide a __Linux GUI__ with all features as in
Windows and Mac OSX and __easy to install packages__ both for servers and
desktop systems.

**THESE SOFTWARE IS UNOFFICIAL AND NOT THE WORK OF BITTORRENT&reg; INC.
PLEASE DO NOT CONTACT THE BITTORRENT&reg; INC. SUPPORT WITH QUESTIONS OR
PROBLEMS RELATED TO THE USE OF THE PACKAGES. YOU WILL FIND COMPETENT HELP
AND SUPPORT IN THE RELATED DISCUSSION THREAD IN THE SUPPORT FORUM (Links
below)**

The mere executables and documentation provided by BitTorrent&reg; Inc. are
distributed in a package named __btsync-common__ - all other packages are
dependent upon it.

The brand new package containing the full featured GUI for BitTorrent Sync for
desktop users is named __btsync-gui__ - This package is going to replace
__btsync-user__ on long term.

The package containing support for BitTorrent Sync as a single or multiple
service with or without WebUI for server/NAS deployment is named __btsync__

The legacy package containing support for BitTorrent Sync as a WebUI and tray
application for desktop users is named __btsync-user__


## Useful Links

- [Project Home Page][2]
- [BitTorrent Sync Home Page][1]
- [BitTorrent Sync Support Forum][3]
  - [Desktop GUI Package Support Thread][4]
  - [Server Package Thread][5]
  - [Legacy Desktop Package Thread][6]

[1]: http://www.bittorrent.com/sync
[2]: http://www.yeasoft.com/site/projects:btsync-deb
[3]: http://forum.bittorrent.com/forum/107-bittorrent-sync/
[4]: http://forum.bittorrent.com/topic/28106-linux-desktop-gui-unofficial-packages-for-bittorrent-sync/
[5]: http://forum.bittorrent.com/topic/18974-debian-and-ubuntu-server-packages-for-bittorrent-sync/
[6]: http://forum.bittorrent.com/topic/19560-debian-and-ubuntu-legacy-desktop-unofficial-packages-for-bittorrent-sync/
