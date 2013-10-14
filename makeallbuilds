#!/bin/bash

set -e

# old stuff
if [ -d btsync ]; then
	pushd btsync
	# make binary targets
	for destarch in i386 amd64 armel armhf powerpc; do
		debuild clean
		debuild -uc -us -b -a${destarch}
		rm -f ../*${destarch}.build
		rm -f ../*${destarch}.changes
	done
	# cleanup garbage
	debuild clean
	# return
	popd
fi


# new stuff
if [ -d btsync-common ]; then
	pushd btsync-common
	# make binary targets
	for destarch in i386 amd64 armel armhf powerpc; do
		debuild clean
		debuild -uc -us -b -a${destarch}
		rm -f ../btsync-common*${destarch}.build
		rm -f ../btsync-common*${destarch}.changes
	done
	# cleanup garbage
	debuild clean
	# return
	popd
else
	echo ERROR: source tree btsync-common not found >&2
fi

set +e
