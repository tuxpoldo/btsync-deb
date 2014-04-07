BitTorrent Sync Server Package
------------------------------

BitTorrent® Inc. delivers for Linux users only a raw binary file without any
deployment concept or setup system. It's up to the user to create a reliable
startup and shutdown logic, manage configuration files, internal storage
directories and everything else related to file and directory permissions,
application update and various other aspects.

The BitTorrent Sync Server Package (`btsync`) is the ideal solution for all
users that want to deploy BitTorrent Sync on Linux servers running Debian or
other derived distributions like Ubuntu, Raspbian, Linux Mint or similar.

__THIS SERVER PACKAGE IS UNOFFICIAL AND NOT THE WORK OF BITTORRENT® INC.
PLEASE DO NOT CONTACT THE BITTORRENT® INC. SUPPORT WITH QUESTIONS OR
PROBLEMS RELATED TO THE USE OF THE PACKAGE. YOU WILL FIND COMPETENT
HELP AND SUPPORT IN THE [SUPPORT FORUM](http://forum.bittorrent.com/topic/18974-debian-and-ubuntu-server-unofficial-packages-for-bittorrent-sync/)__


### Typical Use Cases ###

The BitTorrent Sync Server Package is designed to run one or more BitTorrent
Sync background processes (called _"instances"_) on servers where no specific
user is usually logged on. Since the server package does not provide any GUI
(except for the optional Web UI provided by BitTorrent Sync itself), it can be
also installed on headless servers (without any desktop environment).

The server version is particularly suitable for the following use cases:

- BitTorrent Sync is used as a background service, to keep directories in sync
  between all servers of a distributed infrastructure like a PXE boot system and
  groups of shared configuration files.
- Always-on instances of BitTorrent Sync for providing an always available
  external copy and source of replicated data for other BitTorrent Sync clients.
- A content distribution network based on shared folders.
- Customized services built upon the functionality of BitTorrent Sync.


### Installation  ###

The most easy and fast way to install the repository is to paste that at a
terminal prompt:

```bash
sh -c "$(curl -fsSL http://debian.yeasoft.net/add-btsync-repository.sh)"
```

The script explains what it will do and then pauses before it does it asking
for your permission. If you encounter any problems or prefer to do it manually,
please __[look here](http://www.yeasoft.com/site/projects:btsync-deb:btsync-repo)__.

Now update the package index and install `btsync` by pasting that at a
terminal prompt

```bash
`which sudo` apt-get update
`which sudo` apt-get install btsync
```

After downloading the packages, the installation begins. The package manager
will ask you, if you want a default instance of BitTorrent Sync to be created.
If you answer __yes__, you will be guided through the installation and when
finished you will have a fully operational BitTorrent Sync instance maintained
by _debconf_. The configuration can be modified and fine tuned at any time by
performing the following command:

```bash
`which sudo` dpkg-reconfigure btsync
```

Here you can also choose to delete the default instance by answering __no__ to
the initial question.


### Usage Notes ###

The BitTorrent Sync Server Package mainly consists of an init-style startup
script that manages every operational aspect of running BitTorrent Sync
instances.


#### Instance Configuration Files ####

All operational parameters for BitTorrent Sync instances are configured in
configuration files located in the directory `/etc/btsync`. These configuration
files basically are [JSON Files](http://en.wikipedia.org/wiki/JSON) and follow
a very strict syntax. In addition to the JSON specification, comments are also
supported. The support of commented lines permits to specify additional
parameters that are not directly parsed by the BitTorrent Sync executable itself
but by the init-script.

The naming convention for configuration files defining BitTorrent Sync instances
is:

```
<instance_name>.conf
```

where `<instance_name>` should be a string consisting of alphanumeric
characters.

The default instance maintained by _debconf_ has also a configuration file that
is named `debconf-default.conf`. This name __shall never be used__ by manually
created configuration files, since it may be deleted or overwritten by
_debconf_. This file __shall also never be edited manually__ since it is often
rewritten and/or created/deleted by _debconf_. If you want to manage the default
instance, you must always use the command:

```bash
`which sudo` dpkg-reconfigure btsync
```

Each configuration file in `/etc/btsync` defines a separate running BitTorrent
Sync _instance_ (that means: a process). When defining more than one instance
on a system, there are some rules that must be considered:

1. The listening ports (parameter `listening_port`) must be unique for each
   BitTorrent Sync instance
2. The internal database path (parameter `storage_path`) must be unique for each
   BitTorrent Sync instance
3. If the Web UI is enabled, the Web UI bind address and listening port
   (parameter `listen`) must be unique for each BitTorrent Sync instance

The syntax and configuration parameters of a BitTorrent Sync configuration file
are partially documented in the example file `/etc/btsync/samples/complex.conf`
and in the [official BitTorrent Sync manual](http://btsync.s3-website-us-east-1.amazonaws.com/BitTorrentSyncUserGuide.pdf)
which can be also found in `/usr/share/doc/btsync-common/BitTorrentSyncUserGuide.pdf.gz`.

There are additional parameters that are parsed by the init script upon startup
and affect many important aspects. These parameters are not parsed directly by
BitTorrent Sync and therefore have to be placed in comment lines. In order to
improve the readability of configuration files, they should be grouped together
and placed at the beginning of the configuration file. The generic syntax of
such parameters is:

```
// PARAMETER_NAME=<parameter value>
```

The following parameters are supported:

- `DAEMON_UID`: A uid (user id) for specifying the user under which the
  BitTorrent Sync instance should run
- `DAEMON_GID`: A gid (group id) for specifying the group under which the
  BitTorrent Sync instance should run
- `DAEMON_UMASK`: The umask (up to 4 octal digits) for the BitTorrent Sync
  instance. If omitted the default umask is used.
- `DAEMON_DEBUG`: The debug mask (4 hex digits) for the BitTorrent Sync
  instance. If omitted the init script will not touch potential settings defined
  manually. If set to `0000`, a potential settings file will be deleted. Full
  detail is set by specifying `FFFF`. The log file can be found in the
  directory specified by `storage_path` and is named `sync.log`
- `DAEMON_NICE`: The niceness level of the BitTorrent Sync instance, which
  affects the process scheduling. Nicenesses range from -20 (most favorable
  scheduling) to 19 (least favorable).
- `DAEMON_BIND`: This parameter works only in conjunction with the package
  `bind-shim`. Please see the specific section below covering the specific
  interface binding topic.

```
//
// DAEMON_UID=jdoe
// DAEMON_UMASK=0002
//
```

This example will launch the instance running under the credentials of the user
"__jdoe__" using __0002__ as umask.

By specifying `DAEMON_UID` and `DAEMON_GID` it is possible to specify under which
credentials the instance runs. In this case it __MUST__ be assured that the
instance is able to read and write all files it must access:

- The instance must be able to read its own configuration file. Since the
  configuration file may contain sensitive data (the userame and password for
  the web interface), it is usually **owned by the user** under which the
  instance runs and has the mode `400 (-r--------)` in order to limit the access 
  to the specific user. Usually the init script takes care of adjusting the file
  permissions.
- The instance must be able to read and write in its `storage_path`, since all
  internal control and status files (and the database of file hashes) are kept
  there. The ideal solution is to keep the `storage_path` somewhere in the home
  directory of the user under which the instance will run. Usually the init 
  script takes care of adjusting the file permissions.
- Obviously the instance must be able to read and write the files and
  directories that will be synchronized.

Some example configuration files are provided under `/etc/btsync/samples`


#### Default Startup Parameters ####

The additional configuration file `/etc/default/btsync` permits to specify
some default startup parameters that may affect every configured instance of
BitTorrent Sync.

The variable **AUTOSTART** defines which instances are started automatically.
It can take the following values:

- `none` No instance is started automatically
- `all` (default) All instances are started automatically
- `<list>` Only the specified instances are started automatically

Instances not started automatically upon system startup can be managed manually
from the command line:

```bash
# start a specific instance
service btsync start <instance_name>
# stop a specific instance
service btsync stop <instance_name>
```

The advanced variable **DAEMON_ARGS** allows to specify additional command line
parameters passed to the daemon. __WARNING__: Be careful!  You should only add
things here if you know __EXACTLY__ what you are doing!

The variable **DAEMON_BIND** has the same purpose as the same parameter in the
instance configuration files, but in this scope it will be applied by default to
all instances. Please see the specific section below covering the specific
interface binding topic.

The variable **DAEMON_INIT_DEBUG** permits to enable extended debug output of
the init-script.

### Binding BitTorrent Sync to a specific interface ###

Unfortunately BitTorrent Sync currently does not support to bind the main
service routine to a specific network interface. Currently only the internal
web server providing the Web UI and the BitTorrent Sync API can be specifically
bound to a specific address.

In order to limit the operation of BitTorrent Sync to a specific interface in a
multihomed environment, a so called [preload shim][1] can be used. The
BitTorrent Sync repository contains a precompiled version of
[Daniel Ryde's bind.so shim](http://www.ryde.net/code/) that must be installed
with:

```bash
`which sudo` apt-get install bind-shim
```

The BitTorrent Sync init script does detect the presence of the library and
enables support for the additional parameter **DAEMON_BIND** that can be
specified either in `/etc/default/btsync` or in instance configuration files.

By specifying a valid TCP/IP address assigned to one of the interfaces of the
system, the BitTorrent Sync instance will bind only to that specific address.
This will affect also the Web UI, if `0.0.0.0` is specified as the bind address.

[1]: https://en.wikipedia.org/wiki/Shim_(computing)

### Some Remarks about Autoupdate ###

The daemon scripts require that autoupdate is disabled in the configuration
script, otherwise the instance will not be started. The reason for that is,
that updates are handled by the Debian/Ubuntu package handling utility itself.



### Compatibility ###

The deb-packages are available for the same architectures as released by
BitTorrent Inc.:

- __i386__ - Intel/AMD 32 Bit
- __amd64__ - Intel/AMD 64 Bit
- __armel__ - ARM EABI
- __armhf__ - ARM hard float
- __powerpc__ - PowerPC

Since the packages still have not been tested on every platform, any
related feedback is highly appreciated.

#### Bug Report, Contribution and Sources ####

If you want to contribute to the development of the packages or if you are
curious how this all works, you may find the current sources of the deployment
scripts and packaging on GitHub (https://github.com/tuxpoldo/btsync-deb)

If you have experienced a reproducible issue that __is related to the
packaging and not to BitTorrent Sync itself__ you are strongly encouraged to
[open an issue on the project's GitHub Page](https://github.com/tuxpoldo/btsync-deb/issues).
Issues related to the native functionality of BitTorrent Sync should instead be
discussed by creating a new topic or partecipating to an already existing topic
in the [BitTorrent Sync Forum](http://forum.bittorrent.com/forum/56-sync-general-discussion/).


