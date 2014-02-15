# coding=utf-8
#
# Copyright 2014 Leo Moll
#
# Authors: Leo Moll and Contributors (see CREDITS)
#
# Thanks to Mark Johnson for btsyncindicator.py which gave me the
# last nudge needed to learn python and write my first linux gui
# application. Tnak you!
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the applicable version of the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License version 3 along with this program.  If not, see
# <http://www.gnu.org/licenses/>
#

from gi.repository import Gtk
from btsyncapi import BtSyncApi
from btsyncutils import *

class BtSyncPrefsAdvanced(BtInputHelper):

	def __init__(self,btsyncapi):
		self.btsyncapi = btsyncapi
		self.prefs = self.btsyncapi.get_prefs()
		self.create()
		print self.prefs

	def create(self):
		# create the dialog object from builder
		self.builder = Gtk.Builder()
		self.builder.add_from_file("prefsadvanced.glade")
		self.builder.connect_signals (self)
		self.dlg = self.builder.get_object('prefsadvanced')
		# get the editing widgets
		self.advancedprefs = self.builder.get_object('advancedprefs')
		self.ap_tree_prefs = self.builder.get_object('ap_tree_prefs')
		self.ap_label_value = self.builder.get_object('ap_label_value')
		self.ap_switch_value = self.builder.get_object('ap_switch_value')
		self.ap_entry_value = self.builder.get_object('ap_entry_value')
		self.ap_reset_value = self.builder.get_object('ap_reset_value')
		# initialize content
		self.doInitEditor()
		self.doInitValues()


	def run(self):
		response = 0
		while response >= 0:
			response = self.dlg.run()
		return response

	def destroy(self):
		self.dlg.destroy()
		del self.builder

	def doInitValues(self):
		self.lock()
		# fill with current values and specifications
		self.advancedprefs.clear()
		for key, value in self.prefs.items():
			valDesc = BtValueDescriptor.new_from(key,value)
			if valDesc.Advanced:
				self.advancedprefs.append([
					str(key), str(value),
					400 if valDesc.is_default(value) else 900,
					valDesc
				]);
		self.unlock()

	def doInitEditor(self,valDesc=None):
		self.lock()
		if valDesc == None:
			self.detach(self.ap_entry_value)
			self.detach(self.ap_switch_value)
			self.ap_label_value.hide()
			self.ap_switch_value.hide()
			self.ap_entry_value.hide()
			self.ap_reset_value.hide()
		else:
			if valDesc.Type == 'b':
				self.attach(self.ap_switch_value,valDesc)
				self.ap_label_value.show()
				self.ap_switch_value.show()
				self.ap_entry_value.hide()
				self.ap_reset_value.show()
			elif valDesc.Type == 'n' or valDesc.Type == 's':
				self.attach(self.ap_entry_value,valDesc)
				self.ap_label_value.show()
				self.ap_switch_value.hide()
				self.ap_entry_value.show()
				self.ap_reset_value.show()
			else:
				self.ap_label_value.hide()
				self.ap_switch_value.hide()
				self.ap_entry_value.hide()
				self.ap_reset_value.hide()
		self.unlock()

	def onSelectionChanged(self,selection):
		model, tree_iter = selection.get_selected()
		self.doInitEditor(None if tree_iter is None else model[tree_iter][3])

	def onSaveEntry(self,widget,valDesc,newValue):
		self.btsyncapi.set_prefs({valDesc.Name : newValue})
		# GtkListStore has no search function. BAD!!! Maybe I'm too stupid?
		for row in self.advancedprefs:
			if row[0] == valDesc.Name:
				row[1] = str(newValue)
				row[2] = valDesc.get_display_width(newValue)
		return True

	def onPrefsAdvancedResetValue(self,widget):
		selection = self.ap_tree_prefs.get_selection()
		model, tree_iter = selection.get_selected()
		if tree_iter is not None:
			# reset to default
			valDesc = model[tree_iter][3]
			self.onSaveEntry(widget,valDesc,valDesc.Default)
			valDesc.set_default()
			self.doInitEditor(valDesc)

