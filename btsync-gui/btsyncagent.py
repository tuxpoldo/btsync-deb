# coding=utf-8
#
# Copyright 2014 Leo Moll
#
# Authors: Leo Moll and Contributors (see CREDITS)
#
# Thanks to Mark Johnson for btsyncindicator.py which gave me the
# last nudge needed to learn python and write my first linux gui
# application. Thank you!
#
# This file is part of btsync-gui. btsync-gui is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

import os
import json
import time
import stat
import signal
import logging
import argparse
import subprocess

from btsyncutils import BtSingleton

class BtSyncAgent:
	# still hardcoded - this is the binary location of btsync when installing
	# the package btsync-common
	BINARY = '/usr/lib/btsync-common/btsync-core'
	# BEWARE: the following API key is owned by tuxpoldo! If you write your own
	#         application, do NOT take this, but request your own key by folling
	#         out the form at http://www.bittorrent.com/sync/developers
	APIKEY = '26U2OU3LNXN4I3QFNT7JAGG5DB676PCZIEL42FBOGYUM4OUMI5YTBNLD64ZXJCLSFWKC'\
		'VOFNPU65UVO5RKSMYJ24A2KX3VPS4S7HICM3U7OI3FUHMXJPSLMBV4XNRKEMNOBDK4I'

	def __init__(self,args):
		self.args = args
		self.uid = int(os.getuid())
		self.pid = None
		self.configpath = os.environ['HOME'] + '/.config/btsync'
		self.storagepath = os.environ['HOME'] + '/.btsync'
		self.pidfile = self.configpath + '/btsync-agent.pid'
		self.conffile = self.configpath + '/btsync-agent.conf'
		self.preffile = self.configpath + '/btsync-gui.prefs'
		self.lockfile = self.configpath + '/btsync-gui.pid'
		self.lock = None
		self.prefs = {}
		# TODO: the automatically started btsync engine, should get randomly
		#       created credentials at each start
		self.username = 'btsync-gui'
		self.password = 'P455w0rD'
		if self.is_auto():
			self.lock = BtSingleton(self.lockfile,'btsync-gui')
		self.load_prefs()

	def __del__(self):
		self.shutdown()

	def set_pref(self,key,value,flush=True):
		self.prefs[key] = value
		if flush:
			self.save_prefs()

	def get_pref(self,key,default):
		return self.prefs.get(key,default)

	def load_prefs(self):
		try:
			pref = open (self.preffile, 'r')
			result = json.load(pref)
			pref.close()
			if isinstance(result,dict):
				self.prefs = result
			else:
				print "Error: " +str(result)
		except Exception as e:
			logging.warning('Error while loading preferences: {0}'.format(e))
			self.prefs = {}
			pass

	def save_prefs(self):
		try:
			pref = open (self.preffile, 'w')
			json.dump(self.prefs,pref)
			pref.close()
			os.chmod(self.preffile, stat.S_IRUSR | stat.S_IWUSR)
		except Exception as e:
			logging.error('Error while saving preferences: {0}'.format(e))
			pass

	def is_auto(self):
		return self.args.host == 'auto'

	def is_primary(self):
		return self.args.host == 'auto' and isinstance(self.lock,BtSingleton)

	def get_lock_filename(self):
		return os.environ['HOME'] + '/.config/btsync/btsync-gui.lock'

	def get_host(self):
		return 'localhost' if self.args.host == 'auto' else self.args.host

	def get_port(self):
		return self.uid + 8999 if self.args.host == 'auto' else self.args.port

	def get_username(self):
		return self.username if self.is_auto() else self.args.username

	def get_password(self):
		return self.password if self.is_auto() else self.args.password

	def get_debug(self):
		if self.args.host == 'auto':
			return os.path.isfile(self.storagepath + '/debug.txt')
		else:
			return False

	def set_debug(self,activate=True):
		if self.args.host == 'auto':
			if activate:
				deb = open (self.storagepath + '/debug.txt', 'w')
				deb.write('FFFF\n')
				deb.close
			else:
				os.remove (self.storagepath + '/debug.txt')

	def startup(self):
		if self.args.host == 'auto':
			# we have to handle everything
			try:
				if not os.path.isdir(self.configpath):
					os.makedirs(self.configpath)
				if not os.path.isdir(self.storagepath):
					os.makedirs(self.storagepath)

				while self.is_running():
					logging.info ('Found running btsync agent. Stopping...')
					os.kill (self.pid, signal.SIGTERM)
					time.sleep(1)
					
				self.make_config_file()
				if not self.is_running():
					logging.info ('Starting btsync agent...')
					subprocess.call([BtSyncAgent.BINARY, '--config', self.conffile])
					time.sleep(0.5)
					if self.is_running():
						# no guarantee that it's already running...
						self.kill_config_file()
			except Exception:
				logging.critical('Failure to start btsync agent - exiting...')
				exit (-1)

	def shutdown(self):
		if self.is_primary() and self.is_running():
			logging.info ('Stopping btsync agent...')
			os.kill (self.pid, signal.SIGTERM)
			self.kill_config_file()

	def make_config_file(self):
		try:
			cfg = open (self.conffile, 'w')
			os.chmod(self.conffile, stat.S_IRUSR | stat.S_IWUSR)
			cfg.write('{\n')
			cfg.write('\t"pid_file" : "{0}",\n'.format(self.pidfile))
			cfg.write('\t"storage_path" : "{0}",\n'.format(self.storagepath))
			# cfg.write('\t"use_gui" : false,\n')
			cfg.write('\t"webui" : \n\t{\n')
			cfg.write('\t\t"listen" : "127.0.0.1:{0}",\n'.format(self.uid + 8999))
			cfg.write('\t\t"login" : "{0}",\n'.format(self.username))
			cfg.write('\t\t"password" : "{0}",\n'.format(self.password))
			cfg.write('\t\t"api_key" : "{}"\n'.format(BtSyncAgent.APIKEY))
			cfg.write('\t}\n')
			cfg.write('}\n')
			cfg.close()
		except Exception:
			logging.critical('Cannot create {0} - exiting...'.format(self.configpath))
			exit (-1)

	def kill_config_file(self):
		if os.path.isfile(self.conffile):
			os.remove(self.conffile)

	def read_pid(self):
		try:
			pid = open (self.pidfile, 'r')
			pidstr = pid.readline().strip('\r\n')
			pid.close()
			self.pid = int(pidstr)
		except Exception:
			self.pid = None
		return self.pid

	def is_running(self):
		self.read_pid()
		if self.pid is None:
			return False
		# very linuxish...
		if not os.path.isdir('/proc/{0}'.format(self.pid)):
			return False
		try:
			pid = open('/proc/{0}/cmdline'.format(self.pid), 'r')
			cmdline = pid.readline()
			pid.close()
			fields = cmdline.split('\0')
			if fields[0] == BtSyncAgent.BINARY:
				return True
			return False
		except Exception:
			return False

