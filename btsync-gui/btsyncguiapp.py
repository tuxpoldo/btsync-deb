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
import dbus
import signal
import locale
import gettext
import logging
import argparse
import subprocess

from gettext import gettext as _
from gi.repository import Gtk

from btsyncagent import BtSyncAgent, BtSyncAgentException, BtSingleInstanceException
from btsyncstatus import *

class GuiApp:

	def __init__(self):
		self.agent = None
		self.indicator = None
		self._init_localisation()
		self._init_argparser()
		self._init_logger()
		try:
			# instantiate agent
			self.agent = BtSyncAgent(self.args)
			# create graceful shutdown mechanisms
			signal.signal(signal.SIGTERM, self.on_signal_term)
			self.bus = dbus.SessionBus()
			self.bus.call_on_disconnection(self.on_session_disconnect)
		except dbus.DBusException as e:
			# basically we can ignore this...
			logging.warning('Failed to connect to session bus: '+str(e))
		except BtSingleInstanceException as e:
			# we are running in auto mode and someone tries to start a
			# second instance
			logging.error(e.message)
			# exit - we cannot tollerate this!
			exit(-1)
		except BtSyncAgentException as e:
			# the agent has already finished his work...
			if e.retcode != 0:
				logging.error(e.message)
			else:
				logging.info(e.message)
				print e.message
			exit (e.retcode)
		except Exception as e:
			# this should not really happen...
			logging.critical('Unexpected exception caught: '+str(e))
			exit(-1)

	def run(self):
		try:
			self.agent.startup()
			# initialize indicator
			self.indicator = BtSyncStatus(self.agent)
			self.indicator.startup()
			# giro giro tondo...
			Gtk.main()
		except Exception as e:
			logging.critical('Unexpected exception caught: '+str(e))
		finally:
			# good night!
			self.shutdown()

	def shutdown(self,returncode=0):
		logging.info('Shutting down application...')
		if self.indicator is not None:
			self.indicator.shutdown()
		if self.agent is not None:
			self.agent.shutdown()
		logging.shutdown()
		exit(returncode)

	def on_session_disconnect(self, connection):
		logging.info('Disconnected from session bus. Shutting down...')
		self.shutdown()

	def on_signal_term(self, signum, frame):
		logging.warning('Signal {0} received. Shutting down...'.format(signum))
		self.shutdown()


	def _init_argparser(self):
		parser = argparse.ArgumentParser()

		parser.add_argument('--log',
					choices=['CRITICAL','ERROR','WARNING','INFO','DEBUG'],
					default='WARNING',
					help=_('Sets the logging level. By default the logging '\
					'level is WARNING'))
		parser.add_argument('--host',
					default='auto',
					help=_('Hostname for the connection to BitTorrent Sync. '\
					'If not specified, a local BitTorrent Sync agent will be '\
					'launched.'))
		parser.add_argument('--port', type=int,
					default=0,
					help=_('Optional port number for the connection to '\
					'BitTorrent Sync. If not specified, port 8888 is taken '\
					'for a connection to a remote BitTorrent Sync agent or '\
					'(8999 + uid) is taken when creating a locally launched '\
					'agent. This option can be made persistent for local '\
					'agents with --savedefaults'))
		parser.add_argument('--username',
					default=None,
					help=_('Optional user name for connecting to a remote '\
					'BitTorrent Sync agent or username to use when creating a '\
					'locally launched agent. This option can be made '\
					'persistent for local agents with --savedefaults'))
		parser.add_argument('--password',
					default=None,
					help=_('Optional password for connecting to a remote '\
					'BitTorrent Sync agent or password to use when creating a '\
					'locally launched agent. This option can be made '\
					'persistent for local agents with --savedefaults'))
		parser.add_argument('--bindui',
					default=None,
					help=_('Optional bind address for the Web UI of a locally '\
					'created BitTorrent Sync agent. By default the agent '\
					'binds to 127.0.0.1. If you want the Web UI of the agent '\
					'to be reachable by other computers, specify one of the '\
					'available IP addresses of this computer or "all" to bind '\
					'to all available adapters. This option can be made '\
					'persistent for local agents with --savedefaults'))
		parser.add_argument('--webui',
					default=False,
					action='store_true',
					help=_('Include the Web UI in the menu. This option can '\
					'be made persistent with --savedefaults'))
		parser.add_argument('--savedefaults',
					action='store_true',
					help=_('If specified, the optionally supplied '\
					'credentials, bind address, port information and storable '\
					'settings will be stored as default in the application '\
					'preferences and used when launching a local BitTorrent '\
					'Sync agent.'))
		parser.add_argument('--cleardefaults',
					action='store_true',
					help=_('If specified, all internally stored credentials, '\
					'bind address, port information and storable settings '\
					'will be cleared from the application preferences.'))
		parser.add_argument('--dark',
					default=False,
					action='store_true',
					help=_('If specified, the dark indicator icon set will '\
					'be used. This option can be made persistent with '\
					'--savedefaults'))

		self.args = parser.parse_args()

	def _init_logger(self):
		# initialize logger
		numeric_level = getattr(logging, self.args.log.upper(), None)
		if not isinstance(numeric_level, int):
			raise ValueError('Invalid log level: %s' % self.args.log)
		logging.basicConfig(level=numeric_level)
		if not os.path.isdir(os.environ['HOME'] + '/.btsync'):
			os.makedirs(os.environ['HOME'] + '/.btsync')
		fh = logging.FileHandler(filename=os.environ['HOME'] + '/.btsync/btsync-gui.log')
		ff = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		fh.setFormatter(ff)
		logging.getLogger().addHandler(fh)
		logging.getLogger().setLevel(numeric_level)

	def _init_localisation(self):
		locale.setlocale(locale.LC_ALL, '')
		# gettext.bindtextdomain('btsync-gui','')
		gettext.textdomain('btsync-gui')



