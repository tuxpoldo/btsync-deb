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
import webbrowser

from gi.repository import Gtk, GObject

from trayindicator import TrayIndicator
from btsyncapp import BtSyncApp
from btsyncutils import BtDynamicTimeout

VERSION = '0.7.1'

class BtSyncStatus:
	DISCONNECTED	= 0
	CONNECTING		= 1
	CONNECTED		= 2
	PAUSED			= 3

	def __init__(self,agent):
		self.builder = Gtk.Builder()
		self.builder.add_from_file(os.path.dirname(__file__) + "/btsyncstatus.glade")
		self.builder.connect_signals (self)
		self.menu = self.builder.get_object('btsyncmenu')
		self.menuconnection = self.builder.get_object('connectionitem')
		self.menustatus = self.builder.get_object('statusitem')
		self.menupause = self.builder.get_object('pausesyncing')
		self.menudebug = self.builder.get_object('setdebug')
		self.menuopenweb = self.builder.get_object('openweb')
		self.menuopenapp = self.builder.get_object('openapp')
		self.about = self.builder.get_object('aboutdialog')


		self.ind = TrayIndicator (
			'btsync',
			'btsync-gui-disconnected'
		)
		if agent.is_auto():
			self.menuconnection.set_visible(False)
			self.ind.set_title('BitTorrent Sync')
			self.ind.set_tooltip_text('BitTorrent Sync Status Indicator')
		else:
			self.menuconnection.set_label('{0}:{1}'.format(agent.get_host(),agent.get_port()))
			self.ind.set_title('BitTorrent Sync {0}:{1}'.format(agent.get_host(),agent.get_port()))
			self.ind.set_tooltip_text('BitTorrent Sync {0}:{1}'.format(agent.get_host(),agent.get_port()))
		self.menuopenweb.set_visible(agent.is_webui())
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
		self.status_to = BtDynamicTimeout(1000,self.btsync_refresh_status)
		self.agent = agent

	def startup(self):
		self.btsyncver = { 'version': '0.0.0' }
		# status
		if self.agent.is_auto():
			self.menupause.set_sensitive(self.agent.is_auto())
			if self.agent.is_paused():
				self.set_status(BtSyncStatus.PAUSED)
				self.menupause.set_active(True)
			else:
				self.set_status(BtSyncStatus.CONNECTING)
				self.menupause.set_active(False)
				self.connect_id = GObject.timeout_add(1000, self.btsync_connect)
		else:
			self.set_status(BtSyncStatus.CONNECTING)
			self.menupause.set_sensitive(False)
			self.menupause.set_active(False)
			self.connect_id = GObject.timeout_add(1000, self.btsync_connect)
		
	def shutdown(self):
		if self.animator_id is not None:
			GObject.source_remove(self.animator_id)
		if self.connect_id is not None:
			GObject.source_remove(self.connect_id)
		self.status_to.stop()

	def open_app(self):
		if isinstance(self.app, BtSyncApp):
			self.app.window.present()
		else:
			try:
				self.app = BtSyncApp(self.agent)
				self.app.connect_close_signal(self.onDeleteApp)
			except requests.exceptions.ConnectionError:
				return self.onConnectionError()
			except requests.exceptions.HTTPError:
				return self.onCommunicationError()

	def close_app(self,stillopen=True):
		if isinstance(self.app, BtSyncApp):
			if stillopen:
				self.app.close()
				# self.app.window.close()
				self.app.window.destroy()
			del self.app
			self.app = None

	def btsync_connect(self):
		if self.connection is BtSyncStatus.DISCONNECTED or \
			self.connection is BtSyncStatus.CONNECTING or \
			self.connection is BtSyncStatus.PAUSED:
			try:
				self.set_status(BtSyncStatus.CONNECTING)
				self.menustatus.set_label('Connecting...')
				version = self.agent.get_version()
				self.btsyncver = version
				self.set_status(BtSyncStatus.CONNECTED)
				self.menustatus.set_label('Idle')
				self.status_to.start()
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
		if self.connection is not BtSyncStatus.CONNECTED:
			logging.info('Interrupting refresh sequence...')
			return False
		logging.info('Refresh status...')
		indexing = False
		transferring = False
		try:
			folders = self.agent.get_folders()
			for fIndex, fValue in enumerate(folders):
				if fValue['indexing'] > 0:
					indexing = True
# this takes too much resources...
#				peers = self.agent.get_folder_peers(fValue['secret'])
#				for pIndex, pValue in enumerate(peers):
#					if long(pValue['upload']) + long(pValue['download']) > 0:
#						transferring = True
#####
			speed = self.agent.get_speed()
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
			return self.onConnectionError()
		except requests.exceptions.HTTPError:
			return self.onCommunicationError()

	def set_status(self,connection,transferring=False):
		if connection is BtSyncStatus.DISCONNECTED:
			self.frame = -1
			self.transferring = False
			self.ind.set_from_icon_name('btsync-gui-disconnected')
			self.menudebug.set_sensitive(False)
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopenapp.set_sensitive(False)
			self.menuopenweb.set_sensitive(False)
		elif connection is BtSyncStatus.CONNECTING:
			self.frame = -1
			self.transferring = False
			self.ind.set_from_icon_name('btsync-gui-connecting')
			self.menudebug.set_sensitive(False)
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopenapp.set_sensitive(False)
			self.menuopenweb.set_sensitive(False)
		elif connection is BtSyncStatus.PAUSED:
			self.frame = -1
			self.transferring = False
			self.ind.set_from_icon_name('btsync-gui-paused')
			self.menudebug.set_sensitive(self.agent.is_local())
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopenapp.set_sensitive(False)
			self.menuopenweb.set_sensitive(False)
		else:
			self.menudebug.set_sensitive(self.agent.is_local())
			self.menudebug.set_active(self.agent.get_debug())
			self.menuopenapp.set_sensitive(True)
			self.menuopenweb.set_sensitive(True)
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
#		self.menu.popup(None,None,Gtk.StatusIcon.position_menu,widget,3,0)
		if self.is_connected():
			self.open_app()

	def onAbout(self,widget):
		self.about.set_version('Version {0} ({0})'.format(self.btsyncver['version']))
		self.about.set_comments('Linux UI Version {0}'.format(VERSION))
		self.about.show()
		self.about.run()
		self.about.hide()

	def onOpenApp(self,widget):
		self.open_app()

	def onOpenWeb(self,widget):
		webbrowser.open('http://{0}:{1}@{2}:{3}'.format(
			self.agent.get_username(),
			self.agent.get_password(),
			self.agent.get_host(),
			self.agent.get_port()
		), 2)

	def onDeleteApp(self, *args):
		self.close_app(False)

	def onSendFeedback(self,widget):
		webbrowser.open(
			'http://forum.bittorrent.com/topic/28106-alpha-full-featured-linux-gui-for-bittorrent-sync-packages-available-for-debian-ubuntu-mint',
			2
		)

	def onOpenManual(self,widget):
		os.system('xdg-open "/usr/share/doc/btsync-common/BitTorrentSyncUserGuide.pdf.gz"')

	def onTogglePause(self,widget):
		if widget.get_active() and not self.agent.is_paused():
			logging.info('Suspending agent...')
			self.close_app();
			self.set_status(BtSyncStatus.PAUSED)
			self.agent.suspend()
		elif not widget.get_active() and self.agent.is_paused():
			logging.info('Resuming agent...')
			self.set_status(BtSyncStatus.CONNECTING)
			self.agent.resume()
			self.connect_id = GObject.timeout_add(1000, self.btsync_connect)

	def onToggleLogging(self,widget):
		if self.is_connected():
			if widget.get_active() and not self.agent.get_debug():
				logging.info('Activate logging...')
				self.agent.set_debug(True)
			elif not widget.get_active() and self.agent.get_debug():
				logging.info('Disable logging...')
				self.agent.set_debug(False)

	def onQuit(self,widget):
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
			self.agent.start_agent()
			self.connect_id = GObject.timeout_add(1000, self.btsync_connect)
		else:
			self.connect_id = GObject.timeout_add(5000, self.btsync_connect)
		return False

	def onCommunicationError(self):
		self.set_status(BtSyncStatus.DISCONNECTED)
		self.menustatus.set_label('Disconnected: Communication Error {0}'.format(self.agent.get_status_code()))
		self.close_app();
		logging.warning('BtSync API HTTP error: {0}'.format(self.agent.get_status_code()))
		self.connect_id = GObject.timeout_add(5000, self.btsync_connect)
		return False


