BitTorrent Sync Server Packages
-------------------------------

If you are using Ubuntu, Debian, Raspian or other derived distributions
based on Debian and you are searching for an easy way to deploy
BitTorrent Sync on your systems, this topic is definitively for you.
Here you will find information about a family of easy to install
deb-packages that offers both a solution for the need of typical
server/cloud operators as for interactive users.

The __server packages__ offer full debconf-support for the automated
creation and maintenance of an optional default configuration as well as
the possibility to manually configure single or multiple BitTorrent Sync
instances with highly customised configurations.

__THESE PACKAGES ARE UNOFFICIAL AND NOT THE WORK OF BITTORRENT® INC.
PLEASE DO NOT CONTACT THE BITTORRENT® INC. SUPPORT WITH QUESTIONS OR
PROBLEMS RELATED TO THE USE OF THE PACKAGES. YOU WILL FIND COMPETENT
HELP AND SUPPORT IN THE [SUPPORT FORUM](http://forum.bittorrent.com/topic/18974-debian-and-ubuntu-server-unofficial-packages-for-bittorrent-sync/)__

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

#### Installation of BitTorrent Sync ####

The installation of btsync is really easy:

```bash
`which sudo` apt-get install btsync
```

After downloading the packages, the installation begins. The package manager
will ask you, if you want a default instance of btsync to be created. If you
say __yes__, you will be guided through the installation and at the end you
will have a fully operational btsync daemon maintained by debconf. The
configuration can be modified and fine tuned at any time by performing the
following command:

```bash
`which sudo` dpkg-reconfigure btsync
```

Here you can select also delete the default instance, by answering __no__ to
the question if you want a default instance to be created.

Beside the presence of a default instance of btsync, the advanced administrator
will be able, to create many instances of btsync, by creating configuration
files in the directory `/etc/btsync`

More details can be found in the usages notes:

### Usage Notes ###

This version of BitTorrent Sync is mainly intended for server usage. It allows
to start one or more BitTorrent Sync daemons based on configuration files
located in `/etc/btsync`

The package installation offers a possibility to create a default instance of
BitTorrent Sync. All relevant parameters can be specified interactively during
the installation. At any time, the configuration of the default instance can be
changed by executing the command:

```bash
`which sudo` dpkg-reconfigure btsync
```

When creating configuration files manually, there are some possibilities to
specify additional configuration parameters.

Configuration parameters not parsed by BitTorrent Sync but by the daemon init
script can be supplied as comments in the configuration file.

The following parameters are supported:

- `DAEMON_UID`: A uid for specifying the user under which the btsync daemon
should run
- `DAEMON_GID`: A gid for specifying the group under which the btsync daemon
should run. If omitted the daemon will run under the primary group of the user
- `DAEMON_UMASK`: The umask (up to 4 octal digits) for the btsync daemon.
If omitted the default umask is used.
- `DAEMON_DEBUG`: The debug mask (4 hex digits) for the btsync daemon.
If omitted the init script will not touch potential settings defined manually.
If set to `0000`, a potential settings file will be deleted. Full detail is
set by specifying `FFFF`

The parameter definition must use an equal sign ("="):

```
//
// DAEMON_UID=jdoe
// DAEMON_UMASK=0002
//
```

This example will launch the instance running under the credentials of the user
"__jdoe__" using __0002__ as umask.

By specifying `<user>` and `<group>` it is possible to specify under which
credentials the daemon runs. In this case it __MUST__ be assured that the
daemon is able to read and write all files he has to access:

- The daemon must be able to read his own configuration file. Since the
configuration file may contain sensitive data (the userame and password for the
web interface), it is usually **owned by the user** under which the daemon runs
and has the mode `400 (-r--------)` in order to limit the access to the
specific user.
- The daemon must be able to read and write in his `storage_path`, since all
internal control and status files (and the database of file hashes) are kept
there. The ideal solution is to keep the storage_path somewhere in the home
directory of the user under which the daemon will run.
- Obviously the daemon must be able to read and write into the directories that
will be synchronized.

Some example configuration files are provided under `/etc/btsync/samples`

The file `/etc/default/btsync` allows to configure the way the daemon starts:

The variable **AUTOSTART** defines which daemons are started automatically.
It can assume the following values:

- `none` No daemon is started automatically
- `all` (default) All daemons are started automatically
- `<list>` Only the specified daemons are started automatically

The variable **DAEMON_ARGS** allows to specify additional command line
parameters passed to the daemon.

Please look also at the sample configuration files installed in
`/etc/btsync/samples`.

The additional configuration file `/etc/default/btsync` permits to specify
which btsync instances should be started automatically and to specify some
additional parameters to pass to the btsync daemon. The default setting is to
start all instances. Additional documentation can be found in the file:

```bash
# This is the configuration file for /etc/init.d/btsync
#
# Start only these btsync instances automatically via
# init script.
# Allowed values are "all", "none" or space separated list of
# names of the instances. If empty, "all" is assumed.
#
# The instance name refers to the btsync configuration file name.
# i.e. "general" would be /etc/btsync/general.conf
#
#AUTOSTART="all"
#AUTOSTART="none"
#AUTOSTART="general special"
#
# Optional arguments to btsync's command line. Be careful!
# You should only add thngs here if you know EXACTLY what
# you are doing!
DAEMON_ARGS=""
#
# Enable this to see more output during the init script
# execution
#DAEMON_INIT_DEBUG=1
```


### Some Remarks about Autoupdate ###

The daemon scripts require that autoupdate is disabled in the configuration
script, otherwise the instance will not be started. The reason for that is,
that updates are handled by the Debian/Ubuntu package handling utility itself.
