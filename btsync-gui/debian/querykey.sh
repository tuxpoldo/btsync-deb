#!/bin/bash

OUTFILE=$1
if [ -z $1 ]; then
	echo "ERROR: outfile must be specified" >&2
	exit 1
fi

# magick shortcut: if you already have a running version of btsync-gui
# installed, you can also build packages without having to enter the
# API key manually...

if [ -f /usr/lib/btsync-gui/btsync-gui.key ]; then
	cat /usr/lib/btsync-gui/btsync-gui.key > ${OUTFILE}
	exit 0
fi


if curl -s -f 'http://www.yeasoft.com/btsync-gui.key' > ${OUTFILE}; then
	# workaround for launchpad - the file is available only at build time
	exit 0
fi

APIKEY=""
printf "Please enter the API key: "
read APIKEY
if [ -z $APIKEY ]; then
	echo "ERROR: Failed to get API key" >&2
	exit 1
fi

echo $APIKEY > ${OUTFILE}
echo "# BEWARE: the following API key is owned by tuxpoldo! If you write your own" >> ${OUTFILE}
echo "#         application, do NOT take this, but request your own key by folling" >> ${OUTFILE}
echo "#         out the form at http://www.bittorrent.com/sync/developers" >> ${OUTFILE}
