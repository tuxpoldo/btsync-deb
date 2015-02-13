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

import logging
from os import environ
from os.path import join as path_join
from os.path import isdir

from gi.repository import Gtk, GObject

try:
	from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
	logging.warning('Ignore the previous error: using Gtk.TrayIcon instead. Everything is fine!') 

class TrayIndicator:
	"""
	This class provides an abstraction of application indicator functionality
	based Gtk.StatusIcon or libindicator3 if the distribution/desktop requires
	it (like Ubuntu with Unity)

	The bindings to libindicator3 are provided by installing the package
	gir1.2-appindicator3-0.1 - the package python-appindicator unfortunately
	provides only PyGtk bindings for Gtk2
	"""
	def __init__(self,name,icon_name,attention_icon_name=None):
		try:
			self.indicator = AppIndicator.Indicator.new (
				name,
				icon_name,
				AppIndicator.IndicatorCategory.APPLICATION_STATUS
			)
			# Try to make AppIndicator respect weird paths in XDG_DATA_DIRS
			for p in environ.get('XDG_DATA_DIRS','').split(':'):
				if p in ('/usr/share', '/usr/local/share'):
					continue
				ip = path_join(p, 'icons')
				if not isdir(ip):
					continue
				self.indicator.set_icon_theme_path(ip)
				break
			if attention_icon_name is None:
				self.indicator.set_attention_icon(icon_name)
			else:
				self.indicator.set_attention_icon(attention_icon_name)
			self.indicator.set_status (AppIndicator.IndicatorStatus.ACTIVE)
			self.statusicn = None
		except NameError:
			self.statusicn = Gtk.StatusIcon()
			self.statusicn.set_name(name)
			self.statusicn.set_from_icon_name(icon_name)
			self.indicator = None
			
	def set_title(self,title):
		if self.indicator is None:
			self.statusicn.set_title(title)

	def	set_tooltip_text(self,text):
		if self.indicator is None:
			self.statusicn.set_tooltip_text(text)

	def set_from_icon_name(self,icon_name):
		if self.indicator is None:
			self.statusicn.set_from_icon_name(icon_name)
		else:
			self.indicator.set_icon(icon_name)

	def set_menu(self,menu):
		self.menu = menu
		if self.indicator is None:
			self.menu = menu
			self.statusicn.connect('popup-menu', self.onContextMenu)
		else:
			self.indicator.set_menu(self.menu)

	def set_default_action(self,handler):
		if self.indicator is None:
			self.statusicn.connect('activate', handler)


	def onContextMenu(self,widget,button,activate_time):
		self.menu.popup(None,None,Gtk.StatusIcon.position_menu,widget,button,activate_time)

