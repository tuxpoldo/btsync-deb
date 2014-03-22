Adding the BitTorrent Sync Repositories
---------------------------------------

Debian and Debian based distributions (Linux Min, Ubuntu, Linspire, Xandros and
Mepis to name a few) use a tool called APT (Advanced Packaging Tool) to manage
all software on the system. The term _"package"_ refers to an individual file
with a `.deb` extension that contains either all or part of an application.

Your distribution comes with some default repositories that are already setup,
but these contain only the software officially distributed by the creator of
your distribution. In order to install the btsync packages, you have to add the
specific repositories where btsync is hosted.

### Install the Repository ###

The most easy and fast way to install the repository is to paste that at a
terminal prompt:

```bash
sh -c "$(curl -fsSL http://debian.yeasoft.net/add-btsync-repository.sh)"
```
 
The script explains what it will do and then pauses before it does it asking
for your permission.

After this, you can directly proceed to the installation.


#### Alternative Manual Installation ####

If you prefer to perform all the steps manually because you really want to
understand what the script is doing, you can also install the repository
manually. The procedure is described hereunder:

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
echo deb http://debian.yeasoft.net/btsync ${CODENAME:-unstable} main > ~/btsync.list
echo deb-src http://debian.yeasoft.net/btsync ${CODENAME:-unstable} main >> ~/btsync.list
unset CODENAME
`which sudo` mv ~/btsync.list /etc/apt/sources.list.d/btsync.list
`which sudo` chown root:root /etc/apt/sources.list.d/btsync.list
`which sudo` apt-get update
```

After this, you can directly proceed to the installation.

#### Alternative for Ubuntu ####

__If you are using Ubuntu__, you may also use the Launchpad PPA instead of the
default repositories but this has __some relevant disadvantages:__

- The PPA only supports Ubuntu versions that are supported (currently lucid,
precise, quantal, saucy and trusty)
- The PPA only supports the __i386__ and __amd64__ architectures
- Often it takes some hours for the packages to be published

If you are OK with this, you can add the Launchpad PPA by issuing the following
commands:

```bash
`which sudo` add-apt-repository ppa:tuxpoldo/btsync
`which sudo` apt-get update
```

After this, you can [directly proceed to the installation](http://www.yeasoft.com/site/projects:btsync-deb).

