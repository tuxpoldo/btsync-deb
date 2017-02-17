#!/bin/bash

set -e

SOURCES="bind-shim btsync-common btsync-core btsync-user btsync-gui btsync"

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
		# clean up garbage
		debuild clean
		# make sure the orig archive exists
		debian/rules get-orig-source
		# make source target
		debuild -S -sa -uc -us
		# cleanup garbage
		debuild clean
		# return
		exit_build
	else
		echo ERROR: source tree ${SRCDIR} not found >&2
	fi
done

set +e
