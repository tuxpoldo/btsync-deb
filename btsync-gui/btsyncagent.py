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
import sys
import json
import time
import stat
import base64
import signal
import logging
import gettext
import argparse
import subprocess

from gettext import gettext as _

from btsyncapi import BtSyncApi
from btsyncutils import BtSingleton, BtSingleInstanceException

class BtSyncAgentException(Exception):
	def __init__(self,retcode,message):
		self.retcode = retcode
		self.message = message
	def __str__(self):
		return repr(self.message)
	def __int__(self):
		return repr(self.retcode)

class BtSyncAgent(BtSyncApi):
	def __init__(self,args):
		BtSyncApi.__init__(self)
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
		# load values from preferences
		self.load_prefs()
		# generate random credentials
		try:
			username = base64.b64encode(os.urandom(16))[:-2]
			password = base64.b64encode(os.urandom(32))[:-2]
		except NotImplementedError:
			logging.warning('No good random generator available. Using default credentials')
			username = 'btsync-ui'
			password = base64.b64encode('This is really not secure!')[:-2]
		self.username = self.get_pref('username',username)
		self.password = self.get_pref('password',password)
		self.bindui = self.get_pref('bindui','127.0.0.1')
		self.portui = self.get_pref('portui',self.uid + 8999)
		self.paused = self.get_pref('paused',False)
		self.webui = self.get_pref('webui',False)
		self.dark = self.get_pref('dark',False)
		# process command line arguments
		if self.args.username is not None:
			self.username = self.args.username
		if self.args.password is not None:
			self.password = self.args.password
		if self.args.bindui is not None:
			self.bindui = '0.0.0.0' if self.args.bindui == 'auto' else self.args.bindui
		if self.args.port != 0:
			self.portui = self.args.port
		if self.args.webui:
			self.webui = self.args.webui
		if self.args.dark:
			self.dark = self.args.dark
		if self.args.cleardefaults:
			# clear saved defaults
			if 'username' in self.prefs:
				del self.prefs['username']
			if 'password' in self.prefs:
				del self.prefs['password']
			if 'webui' in self.prefs:
				del self.prefs['webui']
			if 'bindui' in self.prefs:
				del self.prefs['bindui']
			if 'portui' in self.prefs:
				del self.prefs['portui']
			if 'dark' in self.prefs:
				del self.prefs['dark']
			self.save_prefs()
			raise BtSyncAgentException(0, _('Default settings cleared.'))
		if self.args.savedefaults:
			# save new defaults
			if self.args.username is not None:
				self.set_pref('username',self.username)
#			else:
#				raise BtSyncAgentException(-1,
#					'Username must be specified when saving defaults')
			if self.args.password is not None:
				self.set_pref('password',self.password)
#			else:
#				raise BtSyncAgentException(-1,
#					'Password must be specified when saving defaults')
			if self.args.bindui is not None:
				# changed bind address for web ui
				self.set_pref('bindui',self.bindui)
			if self.args.port != 0:
				# changed bind port for web ui
				self.set_pref('portui',self.portui)
			if self.args.webui:
				self.set_pref('webui',self.args.webui)
			if self.args.dark:
				self.set_pref('dark',self.args.dark)
			raise BtSyncAgentException(0, _('Default settings saved.'))
		# initialize btsync api
		self.set_connection_params(
			host = self.get_host(), port = self.get_port(),
			username = self.get_username(), password = self.get_password()
		)
		if self.is_auto():
			self.lock = BtSingleton(self.lockfile,'btsync-gui')

	def __del__(self):
		self.shutdown()

	def startup(self):
		if self.args.host == 'auto':
			# we have to handle everything
			try:
				# Force-search for the binary so we can quit before trying
				# anything if its not there
				self.get_binary()

				self.make_local_paths()

				while self.is_running():
					logging.info ('Found running btsync agent. Stopping...')
					os.kill (self.pid, signal.SIGTERM)
					time.sleep(1)

				if not self.is_paused():
					logging.info ('Starting btsync agent...')
					self.start_agent()
			except Exception:
				logging.critical('Failure to start btsync agent - exiting...')
				exit (-1)

	def suspend(self):
		if self.args.host == 'auto':
			if not self.paused:
				self.paused = True
				self.set_pref('paused', True)
				logging.info ('Suspending btsync agent...')
				if self.is_running():
					self.kill_agent()

	def resume(self):
		if self.args.host == 'auto':
			if self.paused:
				self.paused = False
				self.set_pref('paused', False)
				logging.info ('Resuming btsync agent...')
				if not self.is_running():
					self.start_agent()

	def shutdown(self):
		if self.is_primary() and self.is_running():
			logging.info ('Stopping btsync agent...')
			self.kill_agent()
			self.kill_config_file()

	def start_agent(self):
		if not self.is_running():
			self.make_config_file()
			subprocess.call([self.get_binary(), '--config', self.conffile])
			time.sleep(0.5)
			if self.is_running():
				# no guarantee that it's already running...
				self.kill_config_file()

	def kill_agent(self):
		BtSyncApi.shutdown(self,throw_exceptions=False)
		time.sleep(0.5)
		if self.is_running():
			try:
				os.kill (self.pid, signal.SIGTERM)
			except OSError:
				# ok the process has stopped before we tried to kill it...
				pass

	def set_pref(self,key,value,flush=True):
		self.prefs[key] = value
		if flush:
			self.save_prefs()

	def get_pref(self,key,default):
		return self.prefs.get(key,default)

	def load_prefs(self):
		if not os.path.isfile(self.preffile):
			self.prefs = {}
			return
		try:
			pref = open (self.preffile, 'r')
			result = json.load(pref)
			pref.close()
			if isinstance(result,dict):
				self.prefs = result
			else:
				print "Error: " + str(result)
		except Exception as e:
			logging.warning('Error while loading preferences: {0}'.format(e))
			self.prefs = {}

	def make_local_paths(self):
		if not os.path.isdir(self.configpath):
			os.makedirs(self.configpath)
		if not os.path.isdir(self.storagepath):
			os.makedirs(self.storagepath)

	def save_prefs(self):
		try:
			self.make_local_paths()
			pref = open (self.preffile, 'w')
			os.chmod(self.preffile, stat.S_IRUSR | stat.S_IWUSR)
			json.dump(self.prefs,pref)
			pref.close()
		except Exception as e:
			logging.error('Error while saving preferences: {0}'.format(e))

	def is_auto(self):
		return self.args.host == 'auto'

	def is_primary(self):
		return self.args.host == 'auto' and isinstance(self.lock,BtSingleton)

	def is_paused(self):
		return self.paused;

	def is_local(self):
		return self.args.host == 'auto' or \
			self.args.host == 'localhost' or \
			self.args.host == '127.0.0.1'

	def is_webui(self):
		return self.webui;

	def get_lock_filename(self):
		return os.environ['HOME'] + '/.config/btsync/btsync-gui.lock'

	def get_host(self):
		return 'localhost' if self.is_auto() else self.args.host

	def get_port(self):
		return self.portui if self.is_auto() else self.args.port if self.args.port != 0 else 8888

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

	def make_config_file(self):
		try:
			cfg = open (self.conffile, 'w')
			os.chmod(self.conffile, stat.S_IRUSR | stat.S_IWUSR)
			cfg.write('{\n')
			cfg.write('\t"pid_file" : "{0}",\n'.format(self.pidfile))
			cfg.write('\t"storage_path" : "{0}",\n'.format(self.storagepath))
			# cfg.write('\t"use_gui" : false,\n')
			cfg.write('\t"i_agree" : "yes",\n')
			cfg.write('\t"webui" : \n\t{\n')
			cfg.write('\t\t"listen" : "{0}:{1}",\n'.format(self.bindui,self.portui))
			cfg.write('\t\t"login" : "{0}",\n'.format(self.username))
			cfg.write('\t\t"password" : "{0}",\n'.format(self.password))
			cfg.write('\t\t"api_key" : "{}"\n'.format(self.get_api_key()))
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
			if fields[0] == self.get_binary():
				return True
			return False
		except Exception:
			return False

	def get_binary(self):
		try:
			if not hasattr(self, '_binary'):
				self._binary = self.find_lib_file(lf_dir='btsync-common',
						lf_name='btsync-core',
						lf_condition=(lambda p: os.access(p, os.X_OK)))
			return self._binary
		except RuntimeError:
			raise BtSyncAgentException(7, 'btsync binary not found')

	@staticmethod
	def get_api_key():
		try:
			kf_path = BtSyncAgent.find_lib_file(lf_dir='btsync-gui',
					lf_name='btsync-gui.key',
					lf_condition=(lambda p: os.access(p, os.R_OK)))
			akf = open(kf_path, 'r')
			key = akf.readline()
			akf.close()
			return key.rstrip('\n\r')
		except (IOError, RuntimeError):
			logging.critical('API Key not found. Stopping application.')
			exit (-1)

	@staticmethod
	def find_lib_file(lf_dir='btsync-common', lf_name='btsync-core',
			lf_condition=(lambda p: os.access(p, os.X_OK))):
		"""
		Search for file in the system libraries

		:param lf_dir       The directory within the system library directory
							where the file is expected to be found
		:param lf_name      Then name of the file to search
		:param lf_condition A function to check additional contitions WRT to
							possible file paths - by default will check if file is
							executalble
		"""
		paths_to_check = []
		files_to_check = [os.path.join(lf_dir, lf_name), lf_name, ]
		if os.path.isabs(__file__):
			paths_to_check.append(os.path.dirname(__file__))
		for p in sys.path:
			paths_to_check.append(p)
			try:
				paths_to_check.append(p[:p.rindex(os.path.sep + 'python')])
			except ValueError:
				pass

		paths_to_check = [os.path.join(p, d) for p in paths_to_check for d in
				files_to_check]

		for p in paths_to_check:
			logging.debug('Looking for %s in %s' % (lf_name, p))
			if os.path.isfile(p) and lf_condition(p):
				return p
		raise RuntimeError('%s not found' % (lf_name))

