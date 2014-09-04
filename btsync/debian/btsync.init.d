#!/bin/sh

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
DESC="P2P file synchronisation daemon(s)"
NAME=btsync
DAEMON=/usr/lib/btsync/btsync-daemon
DAEMON_BINARY=btsync-daemon
DAEMON_ARGS=""
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

test -d $CONFIG_DIR || exit 0

set +e

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

log_info_msg () {
	echo "$@"
	log_message "info" "$@"
}

log_error_msg () {
	log_failure_msg "$@"
	log_message "err" "$@"
}

config_debug () {
	if [ $DAEMON_INIT_DEBUG ]; then
		log_info_msg "== COMMAND: ${1} ==========================="
		log_info_msg "File Name: '$CONFFILE'"
		log_info_msg "Name Part: '$BASENAME'"
		log_info_msg "Credential Part: '$CREDENTIALS'"
		log_info_msg "Run As User: '$CRED_UID'"
		log_info_msg "Run As Group: '$CRED_GID'"
		log_info_msg "Run with umask: '$UMASK'"
		log_info_msg "Storage Path: '$STORAGE_PATH'"
		log_info_msg "PID File: '$PID_FILE'"
		log_info_msg "Debug flags: '$DMASK'"
		log_info_msg "Nice level: '$NICE_LEVEL'"
	    if [ "${DAEMON_ADDR}" != "0.0.0.0" ]; then
			log_info_msg "Bind address: '$DAEMON_ADDR'"
		elif [ -n "${DAEMON_BIND}" ]; then
			log_info_msg "Bind address: '$DAEMON_BIND'"
		fi
	fi
}

config_from_conffile () {
	# $1 : config file
	BASENAME=${1%%.*${CONFIG_EXT}}
	# old method: credentials encoded into the filename
	CREDENTIALS=`expr match "${1}" ${BASENAME}'\.\([a-z,0-9,_,\.,-]*\)\.'${CONFIG_EXT}`
	CRED_UID=`expr match "${CREDENTIALS}" '\([^\.]*\)'`
	CRED_GID=`expr match "${CREDENTIALS}" '.*\.\([^\.]*\)'`
	CREDENTIALS=`echo "${CREDENTIALS}" | tr "." ":"`
	# new method: credentials encoded in comments in the config file
	#             if found this supersedes credentials encoded into
	#             the filename
	if grep -w 'DAEMON_[UI]ID' ${CONFIG_DIR}/$1 > /dev/null; then
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
	CRED_UID=${CRED_UID:-root}
	CRED_GID=${CRED_GID:-root}
	# umask encoded in comments in the config file
	UMASK=$(grep 'DAEMON_UMASK[ \t]*=' ${CONFIG_DIR}/$1 | cut -d= -f 2 | sed -e "s/ //g" -e "s/\t//g")
	UMASK=$(expr match "${UMASK}" '\([0-7]\{1,4\}\)')
	UMASK=${UMASK:-$(umask)}
	# debug mask encoded in comments in the config file
	DMASK=$(grep 'DAEMON_DEBUG[ \t]*=' ${CONFIG_DIR}/$1 | cut -d= -f 2 | sed -e "s/ //g" -e "s/\t//g")
	DMASK=$(expr match "${DMASK}" '\([0-9,A-F,a-f][0-9,A-F,a-f][0-9,A-F,a-f][0-9,A-F,a-f]\)' | tr "[a-f]" "[A-F]")
	# nice level encoded in comments in the config file
	NICE_LEVEL=$(grep 'DAEMON_NICE[ \t]*=' ${CONFIG_DIR}/$1 | cut -d= -f 2 | sed -e "s/ //g" -e "s/\t//g")
	NICE_LEVEL=$(expr match "${NICE_LEVEL}" '\(-\{0,1\}+\{0,1\}[0-9]\{1,2\}\)')
	NICE_LEVEL=${NICE_LEVEL:-0}
	# bind address of the daemon
	DAEMON_ADDR=$(grep 'DAEMON_BIND[ \t]*=' ${CONFIG_DIR}/$1 | cut -d= -f 2 | sed -e "s/ //g" -e "s/\t//g")
	DAEMON_ADDR=$(expr match "${DAEMON_ADDR}" '\([0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\)')
	DAEMON_ADDR=${DAEMON_ADDR:-0.0.0.0}
	# storage_path as saved in config file. This parameter is mandatory
	STORAGE_PATH=$(grep '^[[:space:]]*"storage_path"' ${CONFIG_DIR}/$1  | cut -d":" -f 2 | cut -d"," -f 1)
	STORAGE_PATH=$(expr match "${STORAGE_PATH}" '^[[:space:]]*"\(.*\)".*')
	# pid_file as saved in config file. If not specified defaults to ${storage_path}/sync.pid
	PID_FILE=$(grep '^[[:space:]]*"pid_file"' ${CONFIG_DIR}/$1  | cut -d":" -f 2 | cut -d"," -f 1)
	PID_FILE=$(expr match "${PID_FILE}" '^[[:space:]]*"\(.*\)".*')
	PID_FILE=${PID_FILE:-${STORAGE_PATH}/sync.pid}
	# load update check setting
	UPDATE_CHECK_DISABLED=$(grep '^[[:space:]]*"check_for_updates"' ${CONFIG_DIR}/$1  | cut -d":" -f 2 | cut -d"/" -f 1 | cut -d"," -f 1 | grep -c false)
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
	BASENAME=$(basename $1 | cut -c8-)
	BASENAME=${BASENAME%%.pid}
	config_from_name "${BASENAME}"
}

test_valid_config () {
	# test for undetected base name (this should never happen)
	if [ -z ${BASENAME} ]; then
		log_error_msg "No instance name detected. Interrupting sequence."
		exit 1
	fi
	# test for duplicate instance name with different credentials.
	# this can only happen with old style credentials encoded into the config file name
	if [ $(ls -l ${CONFIG_DIR}/${BASENAME}.${CONFIG_EXT} ${CONFIG_DIR}/${BASENAME}.*.${CONFIG_EXT} 2> /dev/null | wc -l) -gt 1 ]; then
		log_error_msg "Duplicate instance name $BASENAME found. Interrupting sequence."
		exit 1
	fi
	# test for disabled update check
	if [ ${UPDATE_CHECK_DISABLED} -ne 1 ]; then
		log_error_msg "Instance name $BASENAME has autoupdate enabled. Interrupting sequence."
		exit 1
	fi
	# test for undetected storage path in config file
	if [ -z ${STORAGE_PATH} ]; then
		log_error_msg "Cannot determine storage path for ${BASENAME}. Interrupting sequence."
		exit 2
	fi
	# test for absolute storage path in config file AND storage path not /
	case $(expr match "${STORAGE_PATH}" '/.*') in
	0)	log_error_msg "Storage path for ${BASENAME} must be absolute. Interrupting sequence."
		exit 1
		;;
	1)	log_error_msg "Storage path for ${BASENAME} cannot be the root of filesystem. Interrupting sequence."
		exit 1
		;;
	*)	;;
	esac
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

adjust_arm_alignment () {
	if [ -r /proc/cpu/alignment ]; then
		if ! $DAEMON --help > /dev/null 2> /dev/null; then
			# something is wrong
			if $DAEMON --help | grep -i "Alignment error" > /dev/null 2> /dev/null; then
				log_info "Changing alignment setting for executing btsync"
				echo 2 > /proc/cpu/alignment
			fi
		fi
	fi
}

adjust_storage_path () {
	# make sure the specified storage path exists....
	mkdir -p "${STORAGE_PATH}"
	# and adapt the ownership of the storage path
	if [ -n "${CREDENTIALS}" ]; then
		chown -R ${CREDENTIALS} "${STORAGE_PATH}"
	fi
	# and adapt the storage path permissions (Closes #122)
	chmod 700 "${STORAGE_PATH}"
	adjust_storage_path_file "${STORAGE_PATH}/settings.dat"
	adjust_storage_path_file "${STORAGE_PATH}/settings.dat.old"
	adjust_storage_path_file "${STORAGE_PATH}/sync.dat"
	adjust_storage_path_file "${STORAGE_PATH}/sync.dat.old"
	adjust_storage_path_file "${STORAGE_PATH}/sync.log"
	adjust_storage_path_file "${STORAGE_PATH}/sync.log.old"
}

adjust_storage_path_file () {
	if [ -f $1 ]; then
		chmod 600 $1
	fi
}

adjust_debug_flags () {
	if [ -z ${STORAGE_PATH} ]; then
		return
	fi
	if [ -n "${DMASK}" ]; then
		if [ "${DMASK}" = "0000" ]; then
			# remove mask specification file
			rm -f "${CREDENTIALS}" "${STORAGE_PATH}/debug.txt"
		else
			if [ ! -d "${STORAGE_PATH}" ]; then
				# initial launch: storage path does not exist
				mkdir -p "${STORAGE_PATH}"
				# make sure the owner is correct
				if [ -n "${CREDENTIALS}" ]; then
					chown "${CREDENTIALS}" "${STORAGE_PATH}"
				fi
			fi
			echo "${DMASK}" > "${STORAGE_PATH}/debug.txt"
			if [ -n "${CREDENTIALS}" ]; then
				chown "${CREDENTIALS}" "${STORAGE_PATH}/debug.txt"
			fi
		fi
	fi
	# ignore mask specification file if DAEMON_DEBUG is not specified
}

shim_begin () {
	# save original values
	OLD_LD_PRELOAD=${LD_PRELOAD}
	OLD_BIND_ADDR=${BIND_ADDR}
	# from /etc/default/btsync
	TRY_ADDR=${DAEMON_BIND}
	if [ "${DAEMON_ADDR}" != "0.0.0.0" ]; then
		# override from config file
		TRY_ADDR=${DAEMON_ADDR}
	fi
	if [ -z ${TRY_ADDR} ]; then
		# nothing to do
		return
	fi
	# check if the shim library is installed
	if [ ! -f /usr/lib/bind.so ]; then
		log_warning_msg "Address bind via shim requested but no shim installed. Install bind-shim first."
		return
	fi
	export LD_PRELOAD=${LD_PRELOAD}:/usr/lib/bind.so
	export BIND_ADDR=${TRY_ADDR}
	return
}

shim_end () {
	LD_PRELOAD=${OLD_LD_PRELOAD}
	BIND_ADDR=${OLD_BIND_ADDR}
	if [ -z ${LD_PRELOAD} ]; then
		unset LD_PRELOAD
	fi
	if [ -z ${BIND_ADDR} ]; then
		unset BIND_ADDR
	fi
}

start_btsync () {
	shim_begin
	config_debug "START"
	log_daemon_msg "${1:-Starting btsync instance '${BASENAME}'}"
	adjust_arm_alignment
	adjust_storage_path
	adjust_debug_flags
	STATUS=0
	start-stop-daemon --start --quiet --oknodo \
		--nicelevel $NICE_LEVEL \
		--pidfile /var/run/$NAME.$BASENAME.pid \
		--make-pidfile ${CREDENTIALS:+--chuid ${CREDENTIALS}} \
		--background ${UMASK:+--umask ${UMASK}} \
		--exec $DAEMON \
		-- --nodaemon --log sync.log --config $CONFIG_DIR/$CONFFILE $DAEMON_ARGS  || STATUS=1

	if [ $STATUS -gt 0 ]; then
		# start-stop-daemon failed. Let's exit immediately
		log_error_msg "Failed to start $NAME instance $BASENAME - please check the configuration file $CONFIG_DIR/$CONFFILE"
		shim_end
		return 1
	fi
	# since btsync does not return an acceptable error
	# code, we must check that it is really running
	WAITCNT=0
	sleep 1
	until test_running $BASENAME; do
		# and wait for the process to come up
		if [ $WAITCNT -ge $TIMEOUT ]; then
			log_error_msg "Failed to start $NAME instance $BASENAME - please check the configuration file $CONFIG_DIR/$CONFFILE"
			shim_end
			STATUS=1
			return 1
		fi
		sleep 1
		WAITCNT=$(($WAITCNT + 1))
	done
	adjust_storage_path
	shim_end
	log_info "$NAME instance $BASENAME started successfully"
	log_end_msg $STATUS
	STATUS=0
}

stop_btsync () {
	config_debug "STOP"
	log_daemon_msg "${1:-Stopping btsync instance '${BASENAME}'}"
	adjust_arm_alignment
	PIDFILE=/var/run/$NAME.$BASENAME.pid
	STATUS=0
	start-stop-daemon --stop --quiet \
		--retry=TERM/30/KILL/5 \
		--exec $DAEMON --pidfile ${PIDFILE}  || STATUS=1
	if [ -f ${PIDFILE} ]; then
		TESTPID=$(cat ${PIDFILE})
		if [ $(( $TESTPID )) -gt 10 ]; then
			if [ ! -f /proc/${TESTPID}/status ]; then
				# remove pid file only if process has really terminated
				rm ${PIDFILE}
			fi
		fi
	fi
	adjust_storage_path
	if [ $STATUS -gt 0 ]; then
		log_error_msg "Failed to stop $NAME instance $BASENAME"
	else
		log_info "$NAME instance $BASENAME stopped successfully"
		log_end_msg $STATUS
	fi
}


case "$1" in
start)
	# autostart btsync instances
	if [ -z "$2" ]; then
		# check if automatic startup is disabled by AUTOSTART=none
		if [ "x$AUTOSTART" = "xnone" -o -z "$AUTOSTART" ]; then
			log_warning_msg "Autostart disabled, no btsync instance will be started."
			exit 0
		fi
		if [ -z "$AUTOSTART" -o "x$AUTOSTART" = "xall" ]; then
			ANYSTARTED=0
			# all btsync instances shall be started automatically
			for CONFFILE in `cd $CONFIG_DIR; ls *.${CONFIG_EXT} 2> /dev/null`; do
				config_from_conffile "${CONFFILE}"
				test_valid_config
				start_btsync "Autostarting btsync instance '$BASENAME'"
				ANYSTARTED=1
			done
			if [ $ANYSTARTED -eq 0 ]; then
				log_warning_msg "No config files found in $CONFIG_DIR - Nothing to start"
			fi
		else
			ANYSTARTED=0
			# start only specified btsync instances
			for BASENAME in $AUTOSTART ; do
				config_from_name "${BASENAME}"
				if [ -f $CONFIG_DIR/$CONFFILE ]; then
					test_valid_config
					start_btsync "Autostarting btsync instance '$BASENAME'"
					ANYSTARTED=1
				else
					log_error_msg "Autostarting btsync instance '$BASENAME': missing $CONFIG_DIR/${BASENAME}.conf file !"
					STATUS=1
				fi
			done
			if [ $ANYSTARTED -eq 0 ]; then
				log_warning_msg "Config file ${BASENAME}.conf found in $CONFIG_DIR - Nothing to start"
			fi
		fi
	else
		# start btsync instances from command line
		while shift ; do
			[ -z "$1" ] && break
			config_from_name "$1"
			if [ -z "$CONFFILE" ]; then
				log_error_msg "Requested btsync instance '$1' does not exist"
				STATUS=1
			elif [ -f $CONFIG_DIR/$CONFFILE ]; then
				test_valid_config
				start_btsync
			else
				log_error_msg "Starting btsync instance '$BASENAME': missing $CONFIG_DIR/$CONFFILE file !"
				STATUS=1
			fi
		done
	fi
	# exit ${STATUS:-0}
	;;
stop)
	if [ -z "$2" ]; then
		PIDFILE=
		for PIDFILE in `ls /var/run/$NAME.*.pid 2> /dev/null`; do
			config_from_pidfile $PIDFILE
			stop_btsync
		done
		if test -z "$PIDFILE" ; then
			log_warning_msg "No btsync instance is running."
		fi
		# the final hammer
		pkill ${DAEMON_BINARY}
	else
		while shift ; do
			[ -z "$1" ] && break
			if [ -f /var/run/$NAME.$1.pid ]; then
				PIDFILE=`ls /var/run/$NAME.$1.pid 2> /dev/null`
				config_from_pidfile $PIDFILE
				stop_btsync
			else
				log_error_msg "Stopping btsync instance '$1': No such btsync instance is running."
			fi
		done
	fi
	# exit ${STATUS:-0}
	;;
status)
	PIDFILE=
	for PIDFILE in `ls /var/run/$NAME.*.pid 2> /dev/null`; do
		config_from_pidfile $PIDFILE
		config_debug "STATUS"
		status_of_proc -p $PIDFILE $(basename $DAEMON) "BTSYNC '${BASENAME}'"
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
