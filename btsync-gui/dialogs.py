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

import os

from gi.repository import Gtk
from btsyncapi import BtSyncApi
from btsyncutils import BtBaseDialog

class BtSyncFolderRemove(BtBaseDialog):
	def __init__(self):
		BtBaseDialog.__init__(self, 'dialogs.glade', 'removefolder')

class BtSyncFolderAdd(BtBaseDialog):
	def __init__(self,btsyncapi):
		BtBaseDialog.__init__(self, 'dialogs.glade', 'addfolder')
		self.btsyncapi = btsyncapi
		self.secret = ''
		self.folder = ''

	def create(self):
		BtBaseDialog.create(self)
		self.secret_w = self.builder.get_object('addfolder_secret')
		self.folder_w = self.builder.get_object('addfolder_folder')

	def run(self):
		while True:
			response = BtBaseDialog.run(self)
			if response == Gtk.ResponseType.CANCEL:
				return response
			elif response == Gtk.ResponseType.OK:
				self.secret = self.secret_w.get_text()
				self.folder = self.folder_w.get_text()
				# test if secret is OK
				if self.btsyncapi.get_error_code(self.btsyncapi.get_secrets(self.secret)) > 0:
					self.show_warning(
						'This secret is invalid.\nPlease generate a new '\
						'secret or enter your shared folder secret.'
					)
				# test if string is an absolute path and a directory
				elif len(self.folder) == 0 or self.folder[0] != '/' or not os.path.isdir(self.folder):
					self.show_warning('Can\'t open the destination folder.')
				# test if the specified directory is readable and writable
				elif not os.access(self.folder,os.W_OK) or not os.access(self.folder,os.R_OK):
					self.show_warning(
						'Don\'t have permissions to write to the selected folder.'
					)
				# test if the specified data is unique
				elif self.is_duplicate_folder(self.folder,self.secret):
					self.show_warning('Selected folder is already added to BitTorrent Sync.')
				else:
					return response

	def is_duplicate_folder(self,folder,secret):
		folders = self.btsyncapi.get_folders()
		if folders is not None:
			for index, value in enumerate(folders):
				if value['dir'] == folder or value['secret'] == secret:
					return True
		return False;


	def onFolderAddChoose(self,widget):
		dialog = Gtk.FileChooserDialog ("Please select a folder to sync", self.dlg,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		)
		if dialog.run() == Gtk.ResponseType.OK:
			self.folder_w.set_text(dialog.get_filename())
		dialog.destroy()

	def onFolderAddGenerate(self,widget):
		secrets = self.btsyncapi.get_secrets()
		self.secret_w.set_text(secrets['read_write'])

