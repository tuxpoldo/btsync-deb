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

import requests

from os.path import dirname

from gi.repository import Gtk
from btsyncapi import BtSyncApi
from prefsadvanced import BtSyncPrefsAdvanced
from btsyncutils import *

class BtSyncApp(BtInputHelper):

	def __init__(self,btsyncapi):
		self.btsyncapi = btsyncapi
		self.builder = Gtk.Builder()
		self.builder.add_from_file(dirname(__file__) + "/btsyncapp.glade")
		self.builder.connect_signals (self)

		self.window = self.builder.get_object('btsyncapp')
		self.window.show()

		self.prefs = self.btsyncapi.get_prefs()
		self.init_folders_controls()
		self.init_folders_values()
		self.init_preferences_controls()
		self.init_preferences_values()

	def connect_close_signal(self,handler):
		return self.window.connect('delete-event', handler)

	def init_folders_controls(self):
		self.folders = self.builder.get_object('folders_list')
		self.folders_treeview = self.builder.get_object('folders_tree_view')
		self.folders_add = self.builder.get_object('folders_add')
		self.folders_remove = self.builder.get_object('folders_add')

	def init_folders_values(self):
		try:
			folders = self.btsyncapi.get_folders()
			if folders is not None:
				for index, value in enumerate(folders):
					self.folders.append ([
						value['dir'],
						'{0} in {1} files'.format(
							self.sizeof_fmt(value['size']),
							str(value['files'])
						)
					])
		except requests.exceptions.ConnectionError:
			return self.onConnectionError()
		except requests.exceptions.HTTPError:
			return self.onCommunicationError()

	def init_preferences_controls(self):
		self.devname = self.builder.get_object('devname')
		self.autostart = self.builder.get_object('autostart')
		self.listeningport = self.builder.get_object('listeningport')
		self.upnp = self.builder.get_object('upnp')
		self.limitdn = self.builder.get_object('limitdn')
		self.limitdnrate = self.builder.get_object('limitdnrate')
		self.limitup = self.builder.get_object('limitup')
		self.limituprate = self.builder.get_object('limituprate')

	def init_preferences_values(self):
		self.lock()
		self.attach(self.devname,BtValueDescriptor.new_from('device_name',self.prefs['device_name']))
		# self.autostart.set_active(self.prefs[""]);
		self.autostart.set_sensitive(False)
		self.attach(self.listeningport,BtValueDescriptor.new_from('listening_port',self.prefs['listening_port']))
		self.attach(self.upnp,BtValueDescriptor.new_from('use_upnp',self.prefs['use_upnp']))
		self.attach(self.limitdnrate,BtValueDescriptor.new_from('download_limit',self.prefs['download_limit']))
		self.attach(self.limituprate,BtValueDescriptor.new_from('upload_limit',self.prefs['upload_limit']))

		self.limitdn.set_active(self.prefs['download_limit'] > 0)
		self.limitup.set_active(self.prefs['upload_limit'] > 0)
		self.unlock()

	def onSaveEntry(self,widget,valDesc,newValue):
		self.btsyncapi.set_prefs({valDesc.Name : newValue})
		self.prefs[valDesc.Name] = newValue
		return True

	def onPreferencesToggledLimitDn(self,widget):
		self.limitdnrate.set_sensitive(widget.get_active())
		if not self.is_locked():
			rate = int(self.limitdnrate.get_text()) if widget.get_active() else 0
			self.btsyncapi.set_prefs({"download_limit" : rate})

	def onPreferencesToggledLimitUp(self,widget):
		self.limituprate.set_sensitive(widget.get_active())
		if not self.is_locked():
			rate = int(self.limituprate.get_text()) if widget.get_active() else 0
			self.btsyncapi.set_prefs({"upload_limit" : rate})

	def onPreferencesClickedAdvanced(self,widget):
		dlgPrefsAdvanced = BtSyncPrefsAdvanced(self.btsyncapi)
		dlgPrefsAdvanced.run()
		dlgPrefsAdvanced.destroy()

	def onConnectionError(self):
		self.window.close()

	def onCommunicationError(self):
		self.window.close()

