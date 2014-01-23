BitTorrent Sync Desktop Packages
--------------------------------

If you are using Ubuntu, Debian, Raspian or other derived distributions
based on Debian and you are searching for an easy way to deploy
BitTorrent Sync on your systems, this topic is definitively for you.
Here you will find information about a family of easy to install
deb-packages that offers both a solution for the need of typical
server/cloud operators as for interactive users.

![BitTorrent Sync Desktop](http://s6.postimg.org/935hs88vl/btsync_user_1.jpg)


The __desktop user packages__ are explicitly intended for __desktop usage__ and
provide a user experience similar to BitTorrent Sync on Windows or Mac OSX by
still giving the user the possibility to customise his installation if he has
special needs.

![BitTorrent Sync Desktop](http://s6.postimg.org/7qnsqcbg1/btsync_user_3.jpg)

__THESE PACKAGES ARE UNOFFICIAL AND NOT THE WORK OF BITTORRENT® INC.
PLEASE DO NOT CONTACT THE BITTORRENT® INC. SUPPORT WITH QUESTIONS OR
PROBLEMS RELATED TO THE USE OF THE PACKAGES. YOU WILL FIND COMPETENT
HELP AND SUPPORT IN THE [SUPPORT FORUM](http://forum.bittorrent.com/topic/19560-debian-and-ubuntu-desktop-unofficial-packages-for-bittorrent-sync/)__

The deb-packages are available for the same architectures as released by
BitTorrent Inc.:

- __i386__ - Intel/AMD 32 Bit
- __amd64__ - Intel/AMD 64 Bit
- __armel__ - ARM EABI
- __armhf__ - ARM hard float
- __powerpc__ - PowerPC

Since the packages still have __not been tested__ with KDE, LXDE, Cinnamon and
Linux Mint, any related feedback is highly appreciated.

#### Bug Report, Contribution and Sources ####

If you want to contribute to the development of the packages or if you are
curious how this all works, you may find the current sources of the deployment
scripts and packaging on GitHub (https://github.com/tuxpoldo/btsync-deb)

The full source of the great indicator applet written by
[Mark Johnson](http://forum.bittorrent.com/user/33710-marxjohnson/) is also
hosted on GitHub (https://github.com/marxjohnson/btsyncindicator)

If you have experienced a reproducible issue that __is related to the
packaging and not to BitTorrent Sync itself__ you are strongly encouraged to
[open an issue on the project's GitHub Page](https://github.com/tuxpoldo/btsync-deb/issues).
Issues related to the native functionality of BitTorrent Sync should instead be
discussed by creating a new topic or partecipating to an already existing topic
in the [BitTorrent Sync Forum](http://forum.bittorrent.com/forum/56-sync-general-discussion/).

#### Adding the Repositories ####

Debian and Debian based distributions (Linspire, Xandros, Ubuntu, and Mepis to
name a few) use a tool called APT (Advanced Packaging Tool) to manage all
software on the system. The term _"package"_ refers to an individual file with
a `.deb` extension that contains either all or part of an application.

Your distribution comes with some default repositories that are already setup,
but these contain only the software officially distributed by the creator of
your distribution. In order to install the btsync packages, you have to add the
specific repositories where btsync is hosted.

__If you are using Ubuntu__, you may also use the Launchpad PPA instead of the
default repositories. Although it is easier to install, there are some
disadvantages:

- The PPA only supports Ubuntu versions that are supported (currently lucid,
precise, quantal, raring, saucy and trusty)
- The PPA only supports the __i386__ and __amd64__ architectures
- Often it takes some hours for the packages to be published

If you are OK with this, you can add the Launchpad PPA by issuing the following
commands:

```bash
`which sudo` add-apt-repository ppa:tuxpoldo/btsync
`which sudo` apt-get update
```

After this, you can directly proceed with the installation.

__If you are not using Ubuntu or you are using an unsupported version or
architecture or by any other reason you prefer the default repositories,
continue here.__

The btsync packages are all signed with a key in order to guarantee their
authenticity. Before using the repository, you should add the key to the
package manager. To do that, run the following command:

```bash
`which sudo` apt-key adv --keyserver keys.gnupg.net --recv-keys 6BF18B15
```

On success you should see an output like this:

```
gpg: requesting key 6BF18B15 from hkp server keys.gnupg.net
gpg: key 6BF18B15: public key "Leo Moll <leo.moll@yeasoft.com>" imported
gpg: no ultimately trusted keys found
gpg: Total number processed: 1
gpg:               imported: 1
```

Now you can easily add the package sources, by executing the following commands:

```bash
CODENAME=$(lsb_release -cs | sed -n '/lucid\|precise\|quantal\|raring\|saucy\|trusty\|squeeze\|wheezy\|jessie\|sid/p')
echo deb http://debian.yeasoft.net/btsync ${CODENAME:-sid} main > ~/btsync.list
echo deb-src http://debian.yeasoft.net/btsync ${CODENAME:-sid} main >> ~/btsync.list
unset CODENAME
`which sudo` mv ~/btsync.list /etc/apt/sources.list.d/btsync.list
`which sudo` chown root:root /etc/apt/sources.list.d/btsync.list
```

Remember to update the local cache:

```bash
`which sudo` apt-get update
```

After that you can proceed with the installation.

#### Installation of the BitTorrent Sync Desktop Version####

The installation of btsync-user is really easy:

```bash
`which sudo` apt-get install btsync-user
```

After the successful installation, you have to initially start BitTorrent Sync.
You have different possibilities to do this:

- Log out and login again. Since BitTorrent Sync is started on logon, it will
start automatically.
- Select _BitTorrent Sync_ from the menu or Unity-Launcher
- Start it from the console by issuing the command:

```
btsync start
```

More details can be found in the usages notes:

### Usage Notes ###

This package of BitTorrent Sync is explicitly intended for generic desktop
usage and provide a user experience similar to BitTorrent Sync on Windows or
Mac OSX: When the user logs in, an instance of BitTorrent Sync is automatically
launched under the user's credentials and a tray applet is launched to show the
status and manage the running instance.

By default the user instance has an automatical created configuration file in
`~/.btsync.conf` and keeps its internal data in the directory `~/.btsync`

A user specific desktop shortcut to the web UI is installed into the system.
Since every user has it's web UI on a different port number, only the desktop
shortcut or the indicator applet should be used to invoke the web UI.

In order to give more freedom to the advanced user, there is also a possibility
to launch BitTorrent Sync with a custom configuration file instead of the
automatically created file: the startup routine of BitTorrent Sync checks,
if there is a file named `btsync.conf` in the home directory of the user.
If `~/btsync.conf` is found, then it is used as configuration file. If not,
BitTorrent Sync uses the automatically created default configuration file
`~/.btsync.conf` that will be recreated on every restart.

The simplest way to create a custom configuration file, is to create a copy of
the default configuration file and then to edit it according to your needs:

```bash
cp ~/.btsync.conf ~/btsync.conf
```

When you are ready with your modifications, you can restart BitTorrent Sync by
executing the command:

```bash
btsync restart
```
 
on the command line.

In addition to the desktop shortcuts and menu functions in the indicator applet,
BitTorrent Sync can also be controlled from the command line using the tool
`btsync`. The tool provides usage instructions by issuing the command:

```bash
btsync -h
```

More comprehensive help can be found on the corresponding manpage:

```bash
man btsync
```
