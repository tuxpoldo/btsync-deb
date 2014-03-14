BitTorrent Sync Desktop GUI Packages
------------------------------------

If you are using Ubuntu, Debian, Raspian or other derived distributions
based on Debian and you are searching for an easy way to deploy
BitTorrent Sync on your systems, this topic is definitively for you.
Here you will find information about a family of easy to install
deb-packages that offers both a solution for the need of typical
server/cloud operators as for interactive users.

![BitTorrent Sync Desktop](http://s6.postimg.org/855mfvgtt/btsync_gui_1.png)

The __desktop gui packages__ are explicitly intended for __desktop usage__ and
provide a user experience similar to BitTorrent Sync on Windows or Mac OSX by
still giving the user the possibility to customise his installation if he has
special needs.

__THESE PACKAGES ARE UNOFFICIAL AND NOT THE WORK OF BITTORRENT® INC.
PLEASE DO NOT CONTACT THE BITTORRENT® INC. SUPPORT WITH QUESTIONS OR
PROBLEMS RELATED TO THE USE OF THE PACKAGES. YOU WILL FIND COMPETENT
HELP AND SUPPORT IN THE [SUPPORT FORUM](http://forum.bittorrent.com/topic/28106-alpha-full-featured-linux-gui-for-bittorrent-sync-packages-available-for-debian-ubuntu-mint/)__

### Compatibility ###

The gui packages are available for the same architectures as released by
BitTorrent Inc.:

- __i386__ - Intel/AMD 32 Bit
- __amd64__ - Intel/AMD 64 Bit
- __armel__ - ARM EABI
- __armhf__ - ARM hard float
- __powerpc__ - PowerPC

The gui packages have been tested on the following distributions:
- __Debian Wheezy__ with __Gnome__ Desktop
- __Ubuntu Raring__ 13.04 with __Unity__ Desktop
- __Linux Mint Petra__ with __Cinnamon__ Desktop

Other users have reported successful installations on:
- __Xubuntu Saucy__ 13.10 with __OpenBox+Tint2__
- __Debian Jessie__ with __KDE__
- __Ubuntu Trusty__ 14.04 with __Cinnamon__, __MATE__ and __OpenBox__
- __Arch Linux__ with __MATE__

The GUI has also been released for other Linux distributions:
- __Arch Linux__: Packages can be found in the [AUR](https://aur.archlinux.org/packages/btsync-gui/)

###### WANTED ######
 
Maintainers for other Linux distributions able to write a suitable packaging
for their favourite distribution:
- __Centos/RHEL__ (rpm)
- __Fedora__ (rpm)
- __SLES__ (rpm)
- __Gentoo__
 
Now it's up to you to test it and give me lots of feedback in order to extend
this list. Any related feedback is highly appreciated.

#### Bug Reports, Contribution and Sources ####

If you want to contribute to the development of the packages or if you are
curious how this all works, you may find the current sources, the deployment
scripts and packaging on GitHub (https://github.com/tuxpoldo/btsync-deb)

If you have experienced a reproducible issue that __is related to the
gui or the packaging and not to BitTorrent Sync itself__ you are strongly
encouraged to [open an issue on the project's GitHub Page](https://github.com/tuxpoldo/btsync-deb/issues).
Issues related to the native functionality of BitTorrent Sync should instead be
discussed by creating a new topic or partecipating to an already existing topic
in the [BitTorrent Sync Forum](http://forum.bittorrent.com/forum/56-sync-general-discussion/).

#### Adding the Repositories ####

Debian and Debian based distributions (Linux Mint, Ubuntu, Linspire, Xandros
and Mepis to name a few) use a tool called APT (Advanced Packaging Tool) to
manage all software on the system. The term _"package"_ refers to an individual
file with a `.deb` extension that contains either all or part of an application.

Your distribution comes with some default repositories that are already setup,
but these contain only the software officially distributed by the creator of
your distribution. In order to install the BitTorrent Sync packages, you have
to add the specific repositories where the BitTorrent Sync packages are hosted.

__If you are using Ubuntu__, you may also use the Launchpad PPA instead of the
default repositories. Although it is easier to install, there are __some
disadvantages:__

- The PPA only supports Ubuntu versions that are supported (currently lucid,
precise, saucy and trusty)
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

The BitTorrent Sync packages are all signed with a key in order to guarantee
their authenticity. Before using the repository, you should add the key to the
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

#### Installation of the BitTorrent Sync Desktop GUI Version ####

The installation of `btsync-gui` is really easy:

```bash
`which sudo` apt-get install btsync-gui
```

On some systems, `libappindicator` is not available or maybe you do not want to
use it. In this case, you may install instead the GTK only version of the
BitTorrent Sync GUI:

```bash
`which sudo` apt-get install btsync-gui-gtk
```

but you can do this only if you are using a GTK based desktop like Gnome on
Debian. __THIS WILL DEFINITIVELY NOT WORK WITH DESKTOPS LIKE UNITY!__ If you
are in doubt, install `btsync-gui` - this will work for sure!

After the successful installation, you have to initially start BitTorrent Sync.
You have various possibilities to do this:

- Log out and login again. Since BitTorrent Sync is started on logon, it will
start automatically.
- Select _BitTorrent Sync_ from the menu or Unity-Launcher

#### Upgrading from btsync-user ####

`btsync-gui` is a drop-in replacement for `btsync-user`. By installing
`btsync-gui` (or `btsync-gui-gtk`), your existing installation of `btsync-user`
will be automatically replaced by `btsync-gui` without losing any data.


### Usage Notes ###

The BitTorrent Sync GUI aims to be a clone of the originall BitTorrent Sync
application on Windows and Mac OSX and to replace on long term the legacy
package `btsync-user`.

The GUI provides two modes of operation:
- __Standalone Mode__: This is the default mode. When the GUI starts, an
  underlaying BitTorrent Sync engine is started too providing an overall
  experience similar to the GUI applications on Windows or Mac OSX.
- __Client Mode__: The GUI can be started from the command line with parameters
  specifying a connection to a remote BitTorrent Sync system. In this case, the
  GUI does not start a local BitTorrent Sync agent, but connects to an already
  running agent at a remote location. __This will work only, if the remote agent 
  has activated API access by specifying a valid API key in the configuration
  file.__

The behaviour of the GUI can be influenced by specifying options on the command
line. There is also a way to make some options persistent across restarts making
it superfluous to specify the options each time you start the GUI.

An overview of the available options:

```
usage: btsync-gui [-h] [--log {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
                  [--host HOST] [--port PORT] [--username USERNAME]
                  [--password PASSWORD] [--bindui BINDUI] [--webui]
                  [--savedefaults] [--cleardefaults]

optional arguments:
  -h, --help            show this help message and exit
  --log {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        Sets the logging level. By default the logging level
                        is WARNING
  --host HOST           Hostname for the connection to BitTorrent Sync. If not
                        specified, a local BitTorrent Sync agent will be
                        launched.
  --port PORT           Optional port number for the connection to BitTorrent
                        Sync. If not specified, port 8888 is taken for a
                        connection to a remote BitTorrent Sync agent or (8999
                        + uid) is taken when creating a locally lauched agent.
                        This option can be made persistent for local agents
                        with --savedefaults
  --username USERNAME   Optional user name for connecting to a remote
                        BitTorrent Sync agent or username to use when creating
                        a locally launched agent. This option can be made
                        persistent for local agents with --savedefaults
  --password PASSWORD   Optional password for connecting to a remote
                        BitTorrent Sync agent or username to use when creating
                        a locally launched agent. This option can be made
                        persistent for local agents with --savedefaults
  --bindui BINDUI       Optional bind address for the Web UI of a locally
                        created BitTorrent Sync agent. By default the agent
                        binds to 127.0.0.1. If you want the Web UI of the
                        agent to be reachable by other computers, specify one
                        of the available IP addresses of this computer or
                        "all" to bind to all available adapters. This option
                        can be made persistent for local agents with
                        --savedefaults
  --webui               Include the Web UI in the menu. This option can be
                        made persistent with --savedefaults
  --savedefaults        If specified, the optionally supplied credentials,
                        bind address and port will be stored as default in the
                        application preferences and used when launching a
                        local BitTorrent Sync agent.
  --cleardefaults       If specified, all internally stored credentials, bind
                        address and port information will be cleared from the
                        application preferences.
```

The usage of the command line options will be explained by example below.

#### Standalone Mode ####

By default there is no way to access the Web UI provided by the BitTorrent Sync
agent, since the agent itself defines at each start random credentials to
protect the system. If you still want to access the Web UI, you can activate an
extended menu option by specifying `--webui` on the command line. You will then
have an additional menu item, that invokes a browser and connects you to the
Web UI.

If you want to make this setting persistent, you can invoke the following
command from the console:

```bash
btsync-gui --webui --savedefaults
```

This makes the setting persistent, and you will not need to specify it again at
each start.

Sometimes it may happen, that you want to access your running BitTorrent Sync
agent from another computer via the Web UI or a `btsync-gui` in Client Mode.
By default this is not possible, because of two reasons:

- The BitTorrent Sync agent binds the administration interface only to the
  loopback adapter making it possible to connect only from the same machine
  (This is a security feature).
- The BitTorrent Sync agent is started at every time with randomly generated
  credentials. Without knowing them, it is impossible to access the
  administration interface of the agent (This is also a security feature).

For users that want to access their system from another computer, there is
still a possibility to configure the GUI in a way that makes the agent
accessible also from other computers. In order to do so, the following
parameters must be changed:

- The BitTorrent Sync agent must bind his administrative interface to all
  adapters of the system or an adapter reachable from outside.
- The BitTorrent Sync agent must bind his administrative interface to a well
  known port. By default the port is the sum of 8999 and the uid of the user.
- The credentials must be set to something known.

The GUI can be launched in such a mode, by specifying the following parameters:

```bash
btsync-gui --bindui 0.0.0.0 --port 10888 --username Leopoldo --password SuperSecret
```

This configures the BitTorrent Sync agent to bind on all interfaces on port
10888 and to be accessinble with the user name "Leopoldo" and the password
"SuperSecret".

Also these settings can be made persistent by adding the option `--savedefaults`

__WARNING:__ as every comfort function, you pay the comfort by lowering the
security. Remember: the product of comfort and security is a constant. You
cannot increase both.


#### Client Mode ####
In client mode, the GUI can be used to access a remotely running BitTorrent
Sync agent. The only prerequisites are that the remote BitTorrent Sync agent is
reachable from your computer, you know the credentials and the API access is
enabled on the remote agent. You can also use the GUI to connect to another
machine where a BitTorrent Sync GUI is running in standalone mode, if you have
configured access possibilities like shown in the example above.

The connection to a remote BitTorrent Sync agent is done by entering the
following command:

```bash
btsync-gui --host myserver.example.com --port 8888 --username Leopoldo --password SuperSecret 
```

If you are able to access the Web UI of a remote BitTorrent Sync system, you
should know everything you need to also launch successfully the GUI.

Since the connection to remote systems is slower, you will notice the following
limitations:

- The refresh rate is slower. It adapts dynamically to the overall performance.
- During the status refreshes, the GUI may be a bit unresponsive.
- There are no local file system checks, when you add a new folder. You must be
  sure, that you enter a valid path on the remote machine.
- Some features are disabled (Pause/resume, Enable/Disable Debug) since they
  are not feasible on remote systems.

