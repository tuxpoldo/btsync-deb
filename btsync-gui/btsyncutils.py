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
import time
import logging
import exceptions

from gi.repository import Gtk, GObject

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

class BtMessageHelper(object):
	def __init__(self):
		self.msgdlg = None

	def show_message(self,parent,messagetext,messagetype=Gtk.MessageType.INFO):
		self.msgdlg = Gtk.MessageDialog (
			parent,
			Gtk.DialogFlags.DESTROY_WITH_PARENT,
			messagetype,
			Gtk.ButtonsType.CLOSE,
			None
		)
		self.msgdlg.set_markup('<b>BitTorrent Sync</b>')
		self.msgdlg.format_secondary_markup(messagetext)
		self.msgdlg.run()
		self.msgdlg.destroy()
		self.msgdlg = None

	def show_warning(self,parent,messagetext):
		self.show_message(parent,messagetext,Gtk.MessageType.WARNING)

	def show_error(self,messagetext):
		self.show_message(parent,messagetext,Gtk.MessageType.ERROR)

class BtBaseDialog(BtMessageHelper):

	def __init__(self,gladefile,dlgname,addobjects = []):
		BtMessageHelper.__init__(self)
		self.gladefile = gladefile
		self.objects = [ dlgname ]
		self.objects.extend(addobjects)
		self.dlg = None

	def create(self):
		# create the dialog object from builder
		self.builder = Gtk.Builder()
		self.builder.add_objects_from_file(os.path.dirname(__file__) + '/' + self.gladefile, self.objects)
		self.builder.connect_signals (self)
		self.dlg = self.builder.get_object(self.objects[0])

	def run(self):
		response = 0
		while response >= 0:
			response = self.dlg.run()
		return response

	def response(self,response_id):
		if self.msgdlg is not None:
			self.msgdlg.response(response_id)
		if self.dlg is not None:
			self.dlg.response(response_id)

	def destroy(self):
		self.dlg.destroy()
		self.dlg = None
		del self.builder

	def show_message(self,messagetext,messagetype=Gtk.MessageType.INFO):
		BtMessageHelper.show_message(self,self.dlg,messagetext,messagetype)

	def show_warning(self,messagetext):
		self.show_message(messagetext,Gtk.MessageType.WARNING)

	def show_error(self,messagetext):
		self.show_message(messagetext,Gtk.MessageType.ERROR)


class BtSingleInstanceException(Exception):

	def __init__(self,message):
		self.message = message
	def __str__(self):
		return repr(self.message)

class BtSingleton():

	def __init__(self,lockfilename,processname):
		self.lockfilename = None
		if os.path.isfile(lockfilename):
			pid = self.readpid(lockfilename)
			if pid is not None and os.path.isfile('/proc/{0}/cmdline'.format(pid)):
				args = self.getcmdline(pid)
				for arg in args:
					if processname in arg:
						raise BtSingleInstanceException('Only one full btsync-gui can run at once')
			# lock file must by a zombie...
			os.remove(lockfilename)
		self.writepid(lockfilename)

	def __del__(self):
		# print "preremove:" + str(self.lockfilename)
		if self.lockfilename and os.path.isfile(self.lockfilename):
			# print "remove:" + str(self.lockfilename)
			os.remove(self.lockfilename)

	def readpid(self,lockfilename):
		try:
			f = open(lockfilename, 'r')
			pid = f.readline().rstrip('\r\n')
			f.close()
			return pid
		except IOError:
			return None

	def writepid(self,lockfilename):
		lockdir = os.path.dirname(lockfilename)
		if lockdir and not os.path.isdir(lockdir):
			os.makedirs(lockdir)
		f = open(lockfilename, 'w')
		f.write(str(os.getpid()))
		f.close()
		self.lockfilename = lockfilename

	def getcmdline(self,pid):
		try:
			f = open('/proc/{0}/cmdline'.format(pid), 'r')
			args = f.readline().split('\0')
			args.append('')
			f.close()
			return args
		except IOError:
			return ['']


class BtDynamicTimeout:

	def __init__(self,interval,function):
		self.mini = interval
		self.last = interval
		self.best = interval
		self.func = function
		self.toid = None

	def start(self):
		if self.toid is None:
			self.toid = GObject.timeout_add(self.best, self._tofunc)

	def stop(self):
		if self.toid is not None:
			GObject.source_remove(self.toid)
			self.toid = None

	def _tofunc(self):
		start = time.time()
		result = self.func()
		if not result:
			self.toid = None
			return False
		duration = int((time.time() - start) * 1000)
		if duration < 50:
			self.best = max(1000,self.mini)
		elif duration < 100:
			self.best = max(2000,self.mini)
		elif duration < 500:
			self.best = max(4000,self.mini)
		else:
			self.best = max(duration * 10,self.mini)
		if self.best != self.last:
			logging.info('Adaptive timeout changed to {0}'.format(self.best))
			self.last = self.best
			self.toid = GObject.timeout_add(self.best, self._tofunc)
			return False
		return True

