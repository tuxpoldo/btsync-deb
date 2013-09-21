#!/bin/sh -e

### BEGIN INIT INFO
# Provides:          btsync
# Required-Start:    $network $remote_fs $syslog
# Required-Stop:     $network $remote_fs $syslog
# Should-Start:      network-manager
# Should-Stop:       network-manager
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: btsync Service
# Description: This script will start btsync service instances as specified
#              in /etc/default/btsync and /etc/btsync/*.conf
### END INIT INFO

# Author: Leo Moll <leo.moll@yeasoft.com>


# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="P2P file synchronisation daemon(s)"       # Introduce a short description here
NAME=btsync                                     # Introduce the short server's name here
DAEMON=/usr/lib/btsync/btsync-daemon            # Introduce the server's location here
DAEMON_ARGS=""                                  # Arguments to run the daemon with
SCRIPTNAME=/etc/init.d/$NAME
CONFIG_DIR=/etc/$NAME
CONFIG_EXT=conf
AUTOSTART="all"
TIMEOUT=5

# Exit if the package is not installed
[ -x $DAEMON ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.0-6) to ensure that this file is present.
. /lib/lsb/init-functions

test $DEBIAN_SCRIPT_DEBUG && set -v -x

test -x $DAEMON || exit 0
test -d $CONFIG_DIR || exit 0

# Source defaults file; edit that file to configure this script.
STATUSREFRESH=10
OMIT_SENDSIGS=0


log_message () {
	if which logger > /dev/null; then
		if [ -z $NAME ]; then
			TOPIC=btsync
		else
			TOPIC=${NAME}.${BASENAME}
		fi
		LEVEL=$1
		shift
		logger -p user.$LEVEL -t $TOPIC "$@"
	fi
}

log_info () {
	log_message "info" "$@"
}

log_warning () {
	log_message "warn" "$@"
}

log_error () {
	log_message "err" "$@"
}

config_from_conffile () {
	# $1 : config file
	set +e
	BASENAME=${1%%.*${CONFIG_EXT}}
	# old method: credentials encoded into the filename
	CREDENTIALS=`expr match "${1}" ${BASENAME}'\.\([a-z,0-9,_,\.,-]*\)\.'${CONFIG_EXT}`
	CRED_UID=`expr match "${CREDENTIALS}" '\([^\.]*\)'`
	CRED_GID=`expr match "${CREDENTIALS}" '.*\.\([^\.]*\)'`
	CREDENTIALS=`echo "${CREDENTIALS}" | tr "." ":"`
	# new method: credentials encoded in comments in the config file
	#             if found this supersedes credentials encoded into
	#             the filename
	if grep 'DAEMON_.ID' ${CONFIG_DIR}/$1 > /dev/null; then
		# credential information found
		CRED_UID=$(grep 'DAEMON_UID[ \t]*=' ${CONFIG_DIR}/$1 | cut -d= -f 2 | sed -e "s/ //g" -e "s/\t//g")
		CRED_GID=$(grep 'DAEMON_GID[ \t]*=' ${CONFIG_DIR}/$1 | cut -d= -f 2 | sed -e "s/ //g" -e "s/\t//g")
		if [ -n "$CRED_UID" -a -n "$CRED_GID" ]; then
			CREDENTIALS="${CRED_UID}:${CRED_GID}"
		elif [ -n "$CRED_UID" ]; then
			CREDENTIALS="${CRED_UID}"
		elif [ -n "$CRED_GID" ]; then
			CREDENTIALS="root:${CRED_GID}"
		else
			CREDENTIALS=""
		fi
	fi
	UMASK=$(grep 'DAEMON_UMASK[ \t]*=' ${CONFIG_DIR}/$1 | cut -d= -f 2 | sed -e "s/ //g" -e "s/\t//g")
	set -e
}

config_from_name () {
	# $1 : name
	unset CONFFILE
	for CONFFILE in `cd $CONFIG_DIR; ls $1.*${CONFIG_EXT} 2> /dev/null`; do
		config_from_conffile ${CONFFILE}
		# take the first one
		break
	done
}

config_from_pidfile () {
	# $1 : pid file
	set +e
	BASENAME=$(basename $1 | cut -c8-)
	BASENAME=${BASENAME%%.pid}
	set -e
	config_from_name "${BASENAME}"
}

test_valid_conffile () {
	# $1 : config file
	set +e
	CHECK=$(grep '^[[:space:]]*"check_for_updates"' $CONFIG_DIR/$1  | cut -d":" -f 2 | cut -d"/" -f 1 | cut -d"," -f 1 | grep -c false)
	if [ $CHECK -ne 1 ]; then
		log_error "Instance name $BASENAME has autoupdate enabled. Interrupting sequence."
		log_failure_msg "Instance name $BASENAME has autoupdate enabled. Interrupting sequence."
		unset CHECK
		exit 1
	fi
	set -e
	unset CHECK
}

test_valid_config () {
	if [ -z "${BASENAME}" ]; then
		log_failure_msg "No instance name detected. Interrupting sequence."
		exit 1
	fi
	if [ -z "${CRED_UID}" ]; then
		CRED_UID="root"
	fi
	if [ -z "${CRED_GID}" ]; then
		CRED_GID="root"
	fi
	if [ -z "{UMASK}" ]; then
		UMASK="$(umask)"
	fi
	set +e
	CHECK=$(ls -l ${CONFIG_DIR}/${BASENAME}*.${CONFIG_EXT} 2> /dev/null | wc -l)
	set -e
	if [ ${CHECK} -gt 1 ]; then
		log_failure_msg "Duplicate instance name $BASENAME found. Interrupting sequence."
		unset CHECK
		exit 1
	fi
	unset CHECK
}

test_running () {
	# Parameters:
	# $1: configuration base name
	# Return:
	# return value 0 if running
	# return value 1 if no pid file
	# return value 2 if pid in pidfile not running
	if [ -f /var/run/${NAME}.${1}.pid ]; then
		TESTPID=$(cat /var/run/${NAME}.${1}.pid)
		if [ $(( $TESTPID )) -gt 10 ]; then
			if [ -f /proc/${TESTPID}/status ]; then
				return 0
			else
				return 2
			fi
		fi
	fi
	return 1
}

start_btsync () {
# debug helpers
#	echo "== START ==========================="
#	echo "File Name: '$CONFFILE'"
#	echo "Name Part: '$BASENAME'"
#	echo "Credential Part: '$CREDENTIALS'"
#	echo "Run As User: '$CRED_UID'"
#	echo "Run As Group: '$CRED_GID'"
#	echo "Run with umask: '$UMASK'"
	STATUS=0
	start-stop-daemon --start --quiet --oknodo \
		--pidfile /var/run/$NAME.$BASENAME.pid \
		--make-pidfile ${CREDENTIALS:+--chuid ${CREDENTIALS}} \
		--background ${UMASK:+--umask ${UMASK}} \
		--exec $DAEMON \
		-- --nodaemon --config $CONFIG_DIR/$CONFFILE $DAEMON_ARGS  || STATUS=1

	if [ $STATUS -gt 0 ]; then
		# start-stop-daemon failed. Let's exit immediately
		log_error "Failed to start $NAME instance $BASENAME - please check the configuration file $CONFIG_DIR/$CONFFILE"
		return 1
	fi
	# since btsync does not return an acceptable error
	# code, we must check that it is really running
	WAITCNT=0
	sleep 1
	until test_running $BASENAME; do
		# and wait for the process to come up
		if [ $WAITCNT -ge $TIMEOUT ]; then
			log_error "Failed to start $NAME instance $BASENAME - please check the configuration file $CONFIG_DIR/$CONFFILE"
			STATUS=1
			return 1
		fi
		sleep 1
		WAITCNT=$(($WAITCNT + 1))
	done
	STATUS=0
}

stop_btsync () {
# debug helpers
#	echo "== STOP ==========================="
#	echo "File Name: '$CONFFILE'"
#	echo "Name Part: '$BASENAME'"
#	echo "Credential Part: '$CREDENTIALS'"
#	echo "Run As User: '$CRED_UID'"
#	echo "Run As Group: '$CRED_GID'"
#	echo "Run with umask: '$UMASK'"
	STATUS=0
	start-stop-daemon --stop --quiet \
		--retry=TERM/30/KILL/5 \
		--exec $DAEMON --pidfile /var/run/$NAME.$BASENAME.pid  || STATUS=1
	rm /var/run/$NAME.$BASENAME.pid
}


case "$1" in
start)
	log_action_begin_msg "Starting $DESC"

	# autostart btsync instances
	if [ -z "$2" ]; then
		# check if automatic startup is disabled by AUTOSTART=none
		if [ "x$AUTOSTART" = "xnone" -o -z "$AUTOSTART" ]; then
			log_warning_msg "Autostart disabled, no btsync instance will be started."
			exit 0
		fi
		if [ -z "$AUTOSTART" -o "x$AUTOSTART" = "xall" ]; then
			# all btsync instances shall be started automatically
			for CONFFILE in `cd $CONFIG_DIR; ls *.${CONFIG_EXT} 2> /dev/null`; do
				config_from_conffile "${CONFFILE}"
				test_valid_conffile "${CONFFILE}"
				test_valid_config
				log_daemon_msg "Autostarting btsync instance '$BASENAME'"
				start_btsync
				log_end_msg $STATUS
			done
		else
			# start only specified btsync instances
			for BASENAME in $AUTOSTART ; do
				config_from_name "${BASENAME}"
				if [ -f $CONFIG_DIR/$CONFFILE ]; then
					test_valid_conffile "${CONFFILE}"
					test_valid_config
					log_daemon_msg "Autostarting btsync instance '$BASENAME'"
					start_btsync
					log_end_msg $STATUS
				else
					log_failure_msg "Autostarting btsync instance '$BASENAME': missing $CONFIG_DIR/$CONFFILE file !"
					STATUS=1
				fi
			done
		fi
	else
		# start btsync instances from command line
		while shift ; do
			[ -z "$1" ] && break
			config_from_name "$1"
			if [ -z "$CONFFILE" ]; then
				log_failure_msg "Requested btsync instance '$1' does not exist"
				STATUS=1
			elif [ -f $CONFIG_DIR/$CONFFILE ]; then
				test_valid_conffile "${CONFFILE}"
				test_valid_config
				log_daemon_msg "Autostarting btsync instance '$BASENAME'"
				start_btsync
				log_end_msg $STATUS
			else
				log_failure_msg "Autostarting btsync instance '$BASENAME': missing $CONFIG_DIR/$CONFFILE file !"
				STATUS=1
			fi
		done
	fi
	# exit ${STATUS:-0}
	;;
stop)
	log_action_begin_msg "Stopping $DESC"
	if [ -z "$2" ]; then
		PIDFILE=
		for PIDFILE in `ls /var/run/$NAME.*.pid 2> /dev/null`; do
			config_from_pidfile $PIDFILE
			log_daemon_msg "Stopping btsync instance '$BASENAME'"
			stop_btsync
			log_end_msg $STATUS
		done
		if test -z "$PIDFILE" ; then
			log_warning_msg "No btsync instance is running."
		fi
	else
		while shift ; do
			[ -z "$1" ] && break
			if [ -f /var/run/$NAME.$1.pid ]; then
				PIDFILE=`ls /var/run/$NAME.$1.pid 2> /dev/null`
				config_from_pidfile $PIDFILE
				log_daemon_msg "Stopping btsync instance '$1'"
				stop_btsync
				log_end_msg $STATUS
			else
				log_failure_msg "Stopping btsync instance '$1': No such btsync instance is running."
			fi
		done
	fi
	# exit ${STATUS:-0}
	;;
status)
	PIDFILE=
	for PIDFILE in `ls /var/run/$NAME.*.pid 2> /dev/null`; do
		set +e
		config_from_pidfile $PIDFILE
		status_of_proc -p $PIDFILE $(basename $DAEMON) "BTSYNC '${BASENAME}'"
		set -e
	done
	;;
restart|force-reload)
	shift
	$0 stop ${@}
	sleep 1
	$0 start ${@}
	;;
*)
	echo "Usage: $0 {start|stop|restart|force-reload|status}" >&2
	exit 1
	;;
esac

exit 0

# vim:set ai sts=2 sw=2 tw=0:
