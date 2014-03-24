BitTorrent Sync Desktop GUI Package
-----------------------------------

BitTorrent® Sync is an excellent product, but as Linux user, you will miss the
easy installation and integrated GUI provided to Windows and Mac OSX users. But
now the dark age is over! Here comes the solution:

![BitTorrent Sync Desktop](http://www.yeasoft.com/assets/images/articles/btsync-gui-1.png)

BitTorrent Sync GUI for Linux (`btsync-gui`) is the _missing link_ for all Linux
desktop users that aims to provide the same user experience as the original
Windows or Mac OSX versions.

If you are using __Arch Linux__, __Debian__, __Ubuntu__, __Linux Mint__ or any
other Debian derived distribution, you will also enjoy the easy to use
installation packages.

__THE SOFTWARE AND THE PACKAGES ARE UNOFFICIAL AND NOT THE WORK OF BITTORRENT®
INC. PLEASE DO NOT CONTACT THE BITTORRENT® INC. SUPPORT WITH QUESTIONS OR
PROBLEMS RELATED TO THE USE OF THE PACKAGES. YOU WILL FIND COMPETENT
HELP AND SUPPORT IN THE [SUPPORT FORUM](http://forum.bittorrent.com/topic/28106-linux-desktop-gui-unofficial-packages-for-bittorrent-sync/)__

#### Installation on Debian and Derivates (Ubuntu, Mint, Raspian, etc) ####

The most easy and fast way to install the repository is to paste that at a
terminal prompt:

```bash
sh -c "$(curl -fsSL http://debian.yeasoft.net/add-btsync-repository.sh)"
```

The script explains what it will do and then pauses before it does it asking
for your permission. If you encounter any problems or prefer to do it manually,
please __[look here](http://www.yeasoft.com/site/projects:btsync-deb:btsync-repo)__.

Now update the package index and install `btsync-gui` by pasting that at a
terminal prompt

```bash
`which sudo` apt-get update
`which sudo` apt-get install btsync-gui
```

On some systems the `AppIndicator` library is not available or maybe you do not
want to use it. In this case, you may install the GTK only version of the
BitTorrent Sync GUI instead:

```bash
`which sudo` apt-get update
`which sudo` apt-get install btsync-gui-gtk
```

Please keep in mind, that __this will work only on GTK based desktops__. If you
install it on other desktops like Unity, `btsync-gui` will start but __you will
see nothing and you have no control over the application!__ Install
`btsync-gui-gtk` only if you know exactly what you are doing!!! If this
happened, you can fix it by installing `btsync-gui` and rebooting your system.

After the successful installation, you have to initially start BitTorrent Sync.
You have various possibilities to do this:

- Log out and login again. Since BitTorrent Sync GUI is registred in the
  autostart group, it will start as soon as you log in.
- Select _BitTorrent Sync_ from the menu or the default application launcher of
  your desktop.


#### Installation on Arch Linux ####

Arch Linux users will find a `btsync-gui` package in the [AUR](https://aur.archlinux.org/packages/btsync-gui/)
The package is maintained by Martin Wimpress (@flexiondotorg) and can be
installed from the AUR using your favourite package manager. e.g.: if you are
using [yaourt](https://wiki.archlinux.org/index.php/yaourt):

```
sudo yaourt -S btsync-gui
```


#### Upgrading from btsync-user ####

`btsync-gui` is a drop-in replacement for `btsync-user`. By installing
`btsync-gui` (or `btsync-gui-gtk`), your existing installation of `btsync-user`
will be automatically replaced by `btsync-gui` without losing any data.


### Usage Notes ###

The BitTorrent Sync GUI aims to be a clone of the original BitTorrent Sync
application on Windows and Mac OSX and to replace on long term the legacy
package `btsync-user`.

If launched without any options, the GUI starts a local BitTorrent Sync agent in
the context of the user and connects to it (standalone mode). The GUI is divided
into two main sections:

- The __status indicator__ is the central access point to BitTorrent Sync and
  shows information about the current status via its icon. The context menu
  allows to perorm some operations and to open the application window.
- The __application window__ allows to manage the shared folders, view the
  connected peers, manage the standard and advanced preferences and connect
  mobile devices via QR-codes with the connection information.

The GUI provides two modes of operation:
- __Standalone Mode__: This is the default mode. When the GUI starts, an
  underlaying BitTorrent Sync agent is started too providing an overall
  experience similar to the GUI applications on Windows or Mac OSX.
- __Client Mode__: The GUI can be started from the command line with parameters
  specifying a connection to a remote BitTorrent Sync agent. In this case, the
  GUI does not start a local BitTorrent Sync agent, but connects to an already
  running agent at a remote location. __This will work only, if the remote agent 
  has activated API access by specifying a valid API key in the configuration
  file.__

The behaviour of the GUI can be influenced by specifying various options on the
command line. There is also a way to make some options persistent across
restarts making it superfluous to specify the options each time you start the
GUI. You can get detailed help about the commandline options by invoking the
man page:

```bash
man btsync-gui
```

Here an overview of the available options:

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
                        BitTorrent Sync agent or password to use when creating
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

The usage of the command line options will be explained by some examples below.

#### Standalone Mode ####

By default there is __no way to access the Web UI__ provided by the BitTorrent
Sync agent, since the agent itself defines at each start random credentials to
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

This example configures the BitTorrent Sync agent to bind on all interfaces on
port 10888 and to be accessible with the user name "Leopoldo" and the password
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

### Compatibility ###

The GUI package is available for the same architectures as released by
BitTorrent Inc.:

- __i386__ - Intel/AMD 32 Bit
- __amd64__ - Intel/AMD 64 Bit
- __armel__ - ARM EABI
- __armhf__ - ARM hard float
- __powerpc__ - PowerPC

The GUI packages has been tested on the following distributions:
- __Debian Wheezy__ with __Gnome__ Desktop
- __Ubuntu Raring__ 13.04 with __Unity__ Desktop
- __Linux Mint Petra__ with __Cinnamon__ Desktop

Users have reported successful installations on:
- __Xubuntu Saucy__ 13.10 with __OpenBox+Tint2__
- __Debian Jessie__ with __KDE__
- __Ubuntu Trusty__ 14.04 with __Cinnamon__, __MATE__ and __OpenBox__
- __Arch Linux__ with __MATE__

The GUI package has also been released for other Linux distributions:
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

