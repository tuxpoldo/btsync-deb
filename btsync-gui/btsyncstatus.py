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
import logging
import requests

from gi.repository import Gtk, GObject

from trayindicator import TrayIndicator
from btsyncapi import BtSyncApi
from btsyncapp import BtSyncApp

VERSION = '0.6'

class BtSyncStatus:
	DISCONNECTED	= 0
	CONNECTING	= 1
	CONNECTED	= 2
	PAUSED		= 3

	def __init__(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file(os.path.dirname(__file__) + "/btsyncstatus.glade")
		self.builder.connect_signals (self)
		self.menu = self.builder.get_object('btsyncmenu')
		self.menustatus = self.builder.get_object('statusitem')
		self.menupause = self.builder.get_object('pausesyncing')
		self.menudebug = self.builder.get_object('setdebug')
		self.menuopen = self.builder.get_object('openapp')
		self.about = self.builder.get_object('aboutdialog')

		self.ind = TrayIndicator (
			'btsync',
			'btsync-gui-disconnected'
		)
		self.ind.set_title('BitTorrent Sync')
		self.ind.set_tooltip_text('BitTorrent Sync Status Indicator')
		self.ind.set_menu(self.menu)
		self.ind.set_default_action(self.onActivate)

		# icon animator
		self.frame = 0
		self.rotating = False
		self.transferring = False
		self.animator_id = None

		# application window
		self.app = None

		# other variables
		self.connection = BtSyncStatus.DISCONNECTED
		self.connect_id = None
		self.status_id = None

	def startup(self,agent):
		self.agent = agent
		# connection
		self.btsyncapi = BtSyncApi(
			host = agent.get_host(), port = agent.get_port(),
			username = agent.get_username(), password = agent.get_password()
		)
		self.btsyncver = { 'version': '0.0.0' }
		# status
		self.set_status(BtSyncStatus.DISCONNECTED)
		self.connect_id = GObject.timeout_add(1000, self.btsync_connect)

	def shutdown(self):
		if self.animator_id is not None:
			GObject.source_remove(self.animator_id)
		if self.connect_id is not None:
			GObject.source_remove(self.connect_id)
		if self.status_id is not None:
			GObject.source_remove(self.status_id)
		del self.agent

	def open_app(self):
		if isinstance(self.app, BtSyncApp):
			self.app.window.present()
		else:
			try:
				self.app = BtSyncApp(self.btsyncapi)
				self.app.connect_close_signal(self.onDeleteApp)
			except requests.exceptions.ConnectionError:
				return self.onConnectionError()
			except requests.exceptions.HTTPError:
				return self.onCommunicationError()

	def close_app(self,stillopen=True):
		if isinstance(self.app, BtSyncApp):
			if stillopen:
				self.app.stop()
				# self.app.window.close()
				self.app.window.destroy()
			del self.app
			self.app = None

	def btsync_connect(self):
		if self.connection is BtSyncStatus.DISCONNECTED:
			try:
				self.set_status(BtSyncStatus.CONNECTING)
				self.menustatus.set_label('Connecting...')
				version = self.btsyncapi.get_version()
				self.btsyncver = version
				self.set_status(BtSyncStatus.CONNECTED)
				self.menustatus.set_label('Idle')
				self.status_id = GObject.timeout_add(1000, self.btsync_refresh_status)
				self.connect_id = None
				return False

			except requests.exceptions.ConnectionError:
				self.connect_id = None
				return self.onConnectionError()
			except requests.exceptions.HTTPError:
				self.connect_id = None
				return self.onCommunicationError()


		else:
			logging.info('Cannot connect since I\'m already connected')
		

	def btsync_refresh_status(self):
		logging.info('Refresh status...')
		indexing = False
		transferring = False
		try:
			folders = self.btsyncapi.get_folders()
			for fIndex, fValue in enumerate(folders):
				if fValue['indexing'] > 0:
					indexing = True
				peers = self.btsyncapi.get_folder_peers(fValue['secret'])
				for pIndex, pValue in enumerate(peers):
					if long(pValue['upload']) + long(pValue['download']) > 0:
						transferring = True
			speed = self.btsyncapi.get_speed()
			if transferring or speed['upload'] > 0 or speed['download'] > 0:
				# there are active transfers...
				self.set_status(BtSyncStatus.CONNECTED,True)
				self.menustatus.set_label('{0:.1f} kB/s up, {1:.1f} kB/s down'.format(speed['upload'] / 1000, speed['download'] / 1000))
			elif indexing:
				self.set_status(BtSyncStatus.CONNECTED)
				self.menustatus.set_label('Indexing...')
			else:
				self.set_status(BtSyncStatus.CONNECTED)
				self.menustatus.set_label('Idle')
			return True
	
		except requests.exceptions.ConnectionError:
			self.status_id = None
			return self.onConnectionError()
		except requests.exceptions.HTTPError:
			self.status_id = None
			return self.onCommunicationError()

	def set_status(self,connection,transferring=False):
		if connection is BtSyncStatus.DISCONNECTED:
			self.frame = -1
			self.transferring = False
			self.ind.set_from_icon_name('btsync-gui-disconnected')
			self.menupause.set_sensitive(False)
			self.menudebug.set_sensitive(False)
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopen.set_sensitive(False)
		elif connection is BtSyncStatus.CONNECTING:
			self.frame = -1
			self.transferring = False
			self.ind.set_from_icon_name('btsync-gui-connecting')
			self.menupause.set_sensitive(False)
			self.menudebug.set_sensitive(False)
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopen.set_sensitive(False)
		elif connection is BtSyncStatus.PAUSED:
			self.frame = -1
			self.transferring = False
			self.ind.set_from_icon_name('btsync-gui-paused')
#			self.menupause.set_sensitive(self.agent.is_auto())
			self.menupause.set_sensitive(False)
			self.menudebug.set_sensitive(self.agent.is_auto())
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopen.set_sensitive(False)
		else:
#			self.menupause.set_sensitive(self.agent.is_auto())
			self.menupause.set_sensitive(False)
			self.menudebug.set_sensitive(self.agent.is_auto())
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopen.set_sensitive(True)
			if transferring and not self.transferring:
				if not self.rotating:
					# initialize animation
					self.transferring = True
					self.frame = 0
					self.animator_id = GObject.timeout_add(200, self.onIconRotate)
			self.transferring = transferring
			if not self.transferring:
				self.ind.set_from_icon_name('btsync-gui-0')
		self.connection = connection

	def show_status(self,statustext):
		self.menustatus.set_label(statustext)

	def is_connected(self):
		return self.connection is BtSyncStatus.CONNECTED

	def onActivate(self,widget):
		self.open_app()
		self.menu.popup(None,None,Gtk.StatusIcon.position_menu,widget,3,0)

	def onAbout(self,widget):
		self.about.set_version('Version {0} ({0})'.format(self.btsyncver['version']))
		self.about.set_comments('Linux UI Version {0}'.format(VERSION))
		self.about.show()
		self.about.run()
		self.about.hide()

	def onTogglePause(self,widget):
		print "onTogglePause"

	def onOpenApp(self,widget):
		self.open_app()

	def onDeleteApp(self, *args):
		self.close_app(False)

	def onToggleLogging(self,widget):
		if self.is_connected():
			if widget.get_active() and not self.agent.get_debug():
				logging.info('Activate logging...')
				self.agent.set_debug(True)
			elif not widget.get_active() and self.agent.get_debug():
				logging.info('Disable logging...')
				self.agent.set_debug(False)

	def onQuit(self,widget):
		if self.agent.is_auto():
			self.btsyncapi.shutdown(throw_exceptions=False)
		Gtk.main_quit()

	def onIconRotate(self):
		if self.frame == -1:
			# immediate stop
			self.frame = 0
			self.rotating = False
			self.animator_id = None
			return False
		elif not self.transferring and self.frame % 12 == 0:
			# do not stop immediately - wait for the
			# cycle to finish.
			self.ind.set_from_icon_name('btsync-gui-0')
			self.rotating = False
			self.frame = 0
			self.animator_id = None
			return False
		else:
			self.ind.set_from_icon_name('btsync-gui-{0}'.format(self.frame % 12))
			self.rotating = True
			self.frame += 1
			return True


	def onConnectionError(self):
		self.set_status(BtSyncStatus.DISCONNECTED)
		self.menustatus.set_label('Disconnected')
		self.close_app();
		logging.info('BtSync API Connection Error')
		if self.agent.is_auto() and not self.agent.is_running():
			logging.warning('BitTorrent Sync seems to be crashed. Restarting...')
			self.agent.startup()
			self.connect_id = GObject.timeout_add(1000, self.btsync_connect)
		else:
			self.connect_id = GObject.timeout_add(5000, self.btsync_connect)
		return False

	def onCommunicationError(self):
		self.set_status(BtSyncStatus.DISCONNECTED)
		self.menustatus.set_label('Disconnected: Communication Error {0}'.format(self.btsyncapi.get_status_code()))
		self.close_app();
		logging.warning('BtSync API HTTP error: {0}'.format(self.btsyncapi.get_status_code()))
		self.connect_id = GObject.timeout_add(5000, self.btsync_connect)
		return False

#	def uptime(self):
#		uptimef = open("/proc/uptime", "r")
#		newupstr = uptimef.read()
#		newuplst = newupstr.split()
#		uptimef.close()
#		return int(float(newuplst[0]) * 1000)

