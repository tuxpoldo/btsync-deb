#!/bin/bash

set -e

SOURCES="btsync-common btsync-gui btsync-user btsync"

[ -n "$1" ] && SOURCES="$1"

function enter_build() {
	pushd $1
	trap exit_build INT QUIT TERM EXIT
}

function exit_build() {
	trap - INT QUIT TERM EXIT
	popd
}

for SRCDIR in ${SOURCES}; do
	if [ -d ${SRCDIR} ]; then
		enter_build ${SRCDIR}
		# make binary targets
		if [ "${SRCDIR}" != "btsync-common" ]; then
			debuild clean
			debuild -uc -us -b
			rm -f ../*all.build
			rm -f ../*all.changes
		else
			for destarch in i386 amd64 armel armhf powerpc kfreebsd-amd64 kfreebsd-i386; do
				debuild clean
				debuild -uc -us -b -a${destarch}
				rm -f ../*${destarch}.build
				rm -f ../*${destarch}.changes
			done
		fi
		# cleanup garbage
		debuild clean
		# return
		exit_build
	else
		echo ERROR: source tree ${SRCDIR} not found >&2
	fi
done

set +e
