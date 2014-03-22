#!/bin/sh
#
# (c) 2014 YeaSoft Int'l - Leo Moll
#
# VERSION 0.1
# This script adds the YeaSoft BitTorrent Sync packaging
# repositories to a machine and also adds the signer key

show_error() {
	echo "error: $*" >&2
}

ask_yesno() {
	ANSWER=
	while [ "$ANSWER" != "yes" -a "$ANSWER" != "no" ]; do
		echo -n "${1} [yes/no] "
		read ANSWER
	done
	if [ "$ANSWER" != "yes" ]; then
		exit ${2:-255}
	fi
}

test_program() {
	if ! which $1 2> /dev/null > /dev/null; then
		show_error $2
		exit 2
	fi
	if [ ! -x `which $1` ]; then
		show_error $2
		exit 2
	fi
}

test_program dpkg "this script can not run on non debian derived distributions."

echo "This script will install the BitTorrent Sync packages repository"
echo "on your machine. Since the BitTorrent Sync packages are all"
echo "signed with a key in order to guarantee their authenticity, an"
echo "additional package signer key will also be installed to your"
echo "machine."
echo

ask_yesno "Do you want to continue with the installation?"

echo
echo "Checking prerequisites..."

SUDO=
if [ $(id -u) -ne 0 ]; then
	SUDO=`which sudo 2> /dev/null`
	if [ -z ${SUDO} ]; then
		show_error "No 'sudo' found on your machine. Since the installation requires"
		show_error "administrative privileges, some operations must be run as root."
		show_error "You can instead try running the script directly as root."
		exit 5
	fi
fi

test_program apt-key "the required tool 'apt-key' cannot be found on your system"

if [ ! -d /etc/apt/sources.list.d ]; then
	show_error "Missing required directory /etc/apt/sources.list.d"
	exit 2
fi

echo "All prerequisites satisfied. Proceeding with installation."
echo

if [ ! -z ${SUDO} ]; then
	echo "During the next steps you may be asked to enter your password"
	echo "in order to confirm some tools to run with administrative"
	echo "privileges."
	echo
fi

echo "Installing package signing key..."
if ! $SUDO apt-key adv --keyserver keys.gnupg.net --recv-keys 6BF18B15; then
	show_error "Package signing key installation failed."
	exit $?
fi
echo

echo "Determining distribution code name..."
if which lsb_release 2> /dev/null > /dev/null; then
	CODENAME=`lsb_release -cs`
	case "${CODENAME}" in
	# detected ubuntu versions
	lucid)		;;
	precise)	;;
	quantal)	;;
	raring)		;;
	saucy)		;;
	trusty)		;;
	# detected debian versions
	squeeze)	;;
	wheezy)		;;
	jessie)		;;
	sid)		;;
	# fallback
	*)		CODENAME=unstable;;
	esac
else
	CODENAME=unstable
fi

echo "Installing repository info..."

echo "# YeaSoft's BitTorrent Sync Packaging Repositoy" > ~/btsync.list.temp
echo "deb http://debian.yeasoft.net/btsync ${CODENAME:-unstable} main" >> ~/btsync.list.temp
echo "deb-src http://debian.yeasoft.net/btsync ${CODENAME:-unstable} main" >> ~/btsync.list.temp

if ! $SUDO mv ~/btsync.list.temp /etc/apt/sources.list.d/btsync.list; then
	rm -f ~/btsync.list.temp
	show_error "Repository info cannot be moved to /etc/apt/sources.list.d"
	exit 5
fi

if ! $SUDO chown root:root /etc/apt/sources.list.d/btsync.list; then
	show_error "Failed to change ownership of /etc/apt/sources.list.d/btsync.list"
	exit 5
fi
echo

echo "Installation completed. The  script has installed the key 6BF18B15"
echo "to the trusted package signers and installed the additional repository"
echo "http://debian.yeasoft.net/btsync with the sources file btsync.list"
echo "located in /etc/apt/sources.list.d"
echo

ask_yesno "Do you want to update the package index now?"

$SUDO apt-get update

echo
echo "Now you are ready to install the BitTorrent Sync package of your choice"
echo
