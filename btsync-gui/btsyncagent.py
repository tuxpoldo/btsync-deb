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
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the applicable version of the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License version 2 along with this program.  If not, see
# <http://www.gnu.org/licenses/>
#

import os
import argparse
import signal
import subprocess
import logging

class BtSyncAgent():
	BINARY = '/usr/lib/btsync-common/btsync-core'
	APIKEY = '26U2OU3LNXN4I3QFNT7JAGG5DB676PCZIEL42FBOGYUM4OUMI5YTBNLD64ZXJCLSFWKCVOFNPU65UVO5RKSMYJ24A2KX3VPS4S7HICM3U7OI3FUHMXJPSLMBV4XNRKEMNOBDK4I'

	def __init__(self,args):
		self.args = args
		self.uid = int(os.getuid())

	def __del__(self):
		self.shutdown()

	def is_ours(self):
		return self.args.host == 'auto'

	def get_host(self):
		return 'localhost' if self.args.host == 'auto' else self.args.host

	def get_port(self):
		return self.uid + 8999 if self.args.host == 'auto' else self.args.port

	def get_username(self):
		return self.args.username

	def get_password(self):
		return self.args.password

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
				self.configpath = os.environ['HOME'] + '/.config/btsync'
				self.storagepath = os.environ['HOME'] + '/.btsync'
				self.pidfile = self.configpath + '/btsync-agent.pid'
				self.conffile = self.configpath + '/btsync-gui.conf'
				if not os.path.isdir(self.configpath):
					os.makedirs(self.configpath)
				if not os.path.isdir(self.storagepath):
					os.makedirs(self.storagepath)
				self.make_config_file()
				if not self.is_running():
					logging.info ('Starting btsync agent...')
					subprocess.call([BtSyncAgent.BINARY, '--config', self.conffile])
			except OSError:
				logging.error('Failure to start btsync agent')
				exit (1)

			except IOError:
				logging.error('Failure to start btsync agent')
				exit (1)

	def shutdown(self):
		if self.is_ours() and self.is_running():
			logging.info ('Stopping btsync agent...')
			os.kill (self.pid, signal.SIGTERM)
			os.remove(self.conffile)

	def make_config_file(self):
		try:
			cfg = open (self.conffile, 'w')
			cfg.write('{\n')
			cfg.write('\t"pid_file" : "{0}",\n'.format(self.pidfile))
			cfg.write('\t"storage_path" : "{0}",\n'.format(self.storagepath))
			cfg.write('\t"webui" : \n\t{')
			cfg.write('\t\t"listen" : "127.0.0.1:{0}",\n'.format(self.uid + 8999))
			cfg.write('\t\t"api_key" : "{}"\n'.format(BtSyncAgent.APIKEY))
			cfg.write('\t}\n')
			cfg.write('}\n')
			cfg.close()
		except IOError:
			logging.error('Cannot create ' + self.configpath)
			exit (1)

	def read_pid(self):
		try:
			pid = open (self.pidfile, 'r')
			pidstr = pid.readline()
			pid.close()
			pidstr.replace('\r', '')
			pidstr.replace('\n', '')
			self.pid = int(pidstr)
		except IOError:
			self.pid = None

	def is_running(self):
		self.read_pid()
		if self.pid is None:
			return False
		# very linuxish...
		if not os.path.isdir('/proc/' + str(self.pid)):
			return False
		try:
			pid = open('/proc/' + str(self.pid) + '/cmdline', 'r')
			cmdline = pid.readline()
			pid.close()
			fields = cmdline.split('\0')
			if fields[0] == BtSyncAgent.BINARY:
				return True
			return False

		except IOError:
			return False
