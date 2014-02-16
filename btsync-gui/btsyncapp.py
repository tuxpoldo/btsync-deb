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
from btsyncapi import BtSyncApi
from prefsadvanced import BtSyncPrefsAdvanced
from btsyncutils import *

class BtSyncApp(BtInputHelper):

	def __init__(self):
		self.btsyncapi = BtSyncApi(port='9999')
		self.builder = Gtk.Builder()
		self.builder.add_from_file("btsyncapp.glade")
		self.builder.connect_signals (self)

		self.window = self.builder.get_object('btsyncapp')
		self.window.show()

		self.prefs = self.btsyncapi.get_prefs()
		self.doPreferencesInitControls()
		self.doPreferencesInitValues()

	def onMainWindowDelete(self, *args):
		Gtk.main_quit(*args)

	def doPreferencesInitControls(self):
		self.devname = self.builder.get_object('devname')
		self.autostart = self.builder.get_object('autostart')
		self.listeningport = self.builder.get_object('listeningport')
		self.upnp = self.builder.get_object('upnp')
		self.limitdn = self.builder.get_object('limitdn')
		self.limitdnrate = self.builder.get_object('limitdnrate')
		self.limitup = self.builder.get_object('limitup')
		self.limituprate = self.builder.get_object('limituprate')

	def doPreferencesInitValues(self):
		self.lock()
		self.attach(self.devname,BtValueDescriptor.new_from('device_name',self.prefs['device_name']))
		# self.autostart.set_active(self.prefs[""]);
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



