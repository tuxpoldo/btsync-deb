#!/usr/bin/env python
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

from gi.repository import Gtk
from btsyncapp import *
from btsyncagent import *
from btsyncstatus import *

import argparse
import logging
import subprocess

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('--log', choices=['CRITICAL','ERROR','WARNING','INFO','DEBUG'],
				default='WARNING',
				help="Set logging level")
	parser.add_argument('--host',
				default='auto',
				help="Hostname for the connection to BitTorrent Sync")
	parser.add_argument('--port', type=int,
				default=8888,
				help="Port number for the connection to BitTorrent Sync")

	parser.add_argument('--username',
				default=None,
				help="Optional user name for the connection to BitTorrent Sync")

	parser.add_argument('--password',
				default=None,
				help="Optional password for the connection to BitTorrent Sync")


	args = parser.parse_args()

	# initialize logger
	numeric_level = getattr(logging, args.log.upper(), None)
	if not isinstance(numeric_level, int):
		raise ValueError('Invalid log level: %s' % args.log)
	logging.basicConfig(level=numeric_level)

	# initialize agent
	agent = BtSyncAgent(args)
	agent.startup()

#	app = BtSyncApp()
	ind = BtSyncStatus()
	ind.startup(agent)
	Gtk.main()

	agent.shutdown()
