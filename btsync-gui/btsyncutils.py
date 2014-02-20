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

from gi.repository import Gtk, GObject

import exceptions

class BtValueDescriptor(GObject.GObject):

	def __init__(self, Name, Type, Value, Default='', Min=None, Max=None, Allowed=None, Forbidden=None, Advanced=True):
		GObject.GObject.__init__(self)
		self.Name	= Name
		self.Type	= Type
		self.Value	= Value
		self.Default	= Default
		self.Min	= Min
		self.Max	= Max
		self.Allowed	= Allowed
		self.Forbidden	= Forbidden
		self.Advanced	= Advanced
		if self.Type == 'n' and self.Allowed is None:
			self.Allowed = '0123456789'
			if str(self.Value)[0:1] == '*':	# remove these stupid "I'm not a default value!"-stars from data
				self.Value = str(self.Value)[1:]
		elif self.Type == 'i' and self.Allowed is None:
			self.Allowed = '-0123456789'
			if str(self.Value)[0:1] == '*':	# remove these stupid "I'm not a default value!"-stars from data
				self.Value = str(self.Value)[1:]
		elif self.Type == 's' and self.Forbidden is None:
			self.Forbidden = '\'"'

	def is_changed(self,value):
		return self.Value != value

	def is_default(self,value):
		return False if self.Default is None else str(self.Default) == str(value)

	def set_default(self):
		self.Value = self.Default

	def get_display_width(self,value):
		return 400 if self.is_default(value) else 900

	def filter_value (self,value):
		newValue = value
		# eliminate non allowed characters
		if self.Forbidden is not None:
			newValue = newValue.strip(self.Forbidden)
		if self.Allowed is not None:
			stripMask = newValue.strip(self.Allowed)
			newValue = newValue.strip(stripMask)
		# boundary check
		if self.Type == 'n' or self.Type == 'i':
			# force boundaries on numerical types
			if self.Min is not None and self._to_num(newValue) < self._to_num(self.Min):
				newValue = self.Min

			if self.Max is not None and self._to_num(newValue) > self._to_num(self.Max):
				newValue = self.Max
		elif self.Type == 's':
			# limit length on string types
			if self.Max is not None and len(newValue) > self._to_num(self.Max):
				newValue = newValue[0:self._to_num(self.Max)]
		return newValue

	@staticmethod
	def new_from(Name,Value=None):
		"""
		This method returns for the specified preferences key a
		suitable BtValueDescriptor
		"""
		return {
		'device_name'				: BtValueDescriptor (Name, 's', Value, Advanced = False), 
		'disk_low_priority'			: BtValueDescriptor (Name, 'b', Value, 1),
		'download_limit'			: BtValueDescriptor (Name, 'n', Value, 0, 0, 1000000, Advanced = False),
		'folder_rescan_interval'		: BtValueDescriptor (Name, 'n', Value, 600, 10, 999999),
		'lan_encrypt_data'			: BtValueDescriptor (Name, 'b', Value, 1),
		'lan_use_tcp'				: BtValueDescriptor (Name, 'b', Value, 0),
		'lang'					: BtValueDescriptor (Name, 'e', Value, 28261, Advanced = False),
		'listening_port'			: BtValueDescriptor (Name, 'n', Value, 0, 1025, 65534, Advanced = False),
		'max_file_size_diff_for_patching'	: BtValueDescriptor (Name, 'n', Value, 1000, 10, 999999),
		'max_file_size_for_versioning'		: BtValueDescriptor (Name, 'n', Value, 1000, 10, 999999),
		'rate_limit_local_peers'		: BtValueDescriptor (Name, 'b', Value, 0),
		'recv_buf_size'				: BtValueDescriptor (Name, 'n', Value, 5, 1, 100),
		'send_buf_size'				: BtValueDescriptor (Name, 'n', Value, 5, 1, 100),
		'sync_max_time_diff'			: BtValueDescriptor (Name, 'n', Value, 600, 0, 999999),
		'sync_trash_ttl'			: BtValueDescriptor (Name, 'n', Value, 30, 0, 999999),
		'upload_limit'				: BtValueDescriptor (Name, 'n', Value, 0, 0, 1000000, Advanced = False),
		'use_upnp'				: BtValueDescriptor (Name, 'b', Value, 1, Advanced = False),
		}.get(Name,BtValueDescriptor (Name, 'u', Value))

	@staticmethod
	def _to_num(value,default=0):
		try:
			return long(value)
		except exceptions.ValueError:
			return default

class BtInputHelper(object):
	assoc	= dict()
	locked	= False

	def __init__(self):
		self.assoc = dict()
		unlock()

	def lock(self):
		self.locked = True

	def unlock(self):
		self.locked = False

	def is_locked(self):
		return self.locked

	def attach(self,widget,valDesc):
		self.detach(widget)
		if valDesc.Type == 'b':
			widget.set_active(int(valDesc.Value) != 0)
			self.assoc[widget] = [
				widget.connect('notify::active',self.onChangedGtkSwitch,valDesc),
				widget.connect('notify::active',self.onSaveGtkSwitch,valDesc)
			]
		elif valDesc.Type == 's' or valDesc.Type == 'n':
			widget.set_text(str(valDesc.Value))
			self.assoc[widget] = [
				widget.connect('changed',self.onChangedGtkEntry,valDesc),
				widget.connect('icon-release',self.onSaveGtkEntry,valDesc)
			]

	def detach(self,widget):
		if widget in self.assoc:
			widget.disconnect(self.assoc[widget][0])
			widget.disconnect(self.assoc[widget][1])
			del self.assoc[widget]

	def sizeof_fmt(self,num):
		for x in ['bytes','KB','MB','GB']:
			if num < 1024.0:
				return "%3.1f %s" % (num, x)
			num /= 1024.0
		return "%3.1f%s" % (num, ' TB')

	def onChangedGtkSwitch(self,widget,unknown,valDesc):
		return

	def onSaveGtkSwitch(self,widget,unknown,valDesc):
		if not self.is_locked() and valDesc.Type == 'b':
			value = 1 if widget.get_active() else 0
			if self.onSaveEntry(widget,valDesc,value):
				valDesc.Value = value

	def onChangedGtkEntry(self,widget,valDesc):
		if not self.locked:
			self.filterEntryContent(widget,valDesc)
			self.handleEntryChanged(widget,valDesc)

	def onSaveGtkEntry(self,widget,iconposition,event,valDesc):
		if not self.is_locked() and iconposition == Gtk.EntryIconPosition.SECONDARY:
			if valDesc.Type == 'b' or valDesc.Type == 'n' or valDesc.Type == 'i':
				value = int(widget.get_text())
			elif valDesc.Type == 's':
				value = widget.get_text()
			else:
				return # unknown type - will not save
			if self.onSaveEntry(widget,valDesc,value):
				valDesc.Value = value
				widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)

	def onSaveEntry(self,widget,valDesc,value):
		return False

	def filterEntryContent (self,widget,valDesc):
		value = widget.get_text()
		newValue = str(valDesc.filter_value(value))
		if newValue != value:
			widget.set_text(newValue)

	def handleEntryChanged(self,widget,valDesc):
		if valDesc is not None and str(valDesc.Value) != widget.get_text():
			widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, 'gtk-save')
		else:
			widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)

## debug stuff
#
#	def _dumpDescriptor(self,valDesc):
#		print "Name:        " + valDesc.Name
#		print "  Type:      " + valDesc.Type
#		print "  Forbidden: " + str(valDesc.Forbidden)
#		print "  Allowed:   " + str(valDesc.Allowed)
#		print "  Min:       " + str(valDesc.Min)
#		print "  Max:       " + str(valDesc.Max)


