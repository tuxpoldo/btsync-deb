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
import qrencode

from gi.repository import Gtk, Gdk, GdkPixbuf
from cStringIO import StringIO
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
		
class BtSyncFolderScanQR(BtBaseDialog):
	def __init__(self,rwsecret,rosecret,basename):
		BtBaseDialog.__init__(self, 'dialogs.glade', 'scanqr')
		self.rwsecret = rwsecret
		self.rosecret = rosecret
		self.basename = basename

	def create(self):
		BtBaseDialog.create(self)
		self.qrcode_image = self.builder.get_object('qrcode_image')
		self.qrcode_fullaccess = self.builder.get_object('qrcode_fullaccess')
		self.qrcode_readaccess = self.builder.get_object('qrcode_readaccess')
		version, size, image = qrencode.encode_scaled(
			'btsync://{0}?n={1}'.format(self.rosecret,self.basename),232
		)
		self.roqrcode = self.image_to_pixbuf(image)

		if self.rwsecret is None:
			self.qrcode_image.set_from_pixbuf(self.roqrcode)
			self.qrcode_readaccess.set_active(True)
			self.qrcode_readaccess.set_sensitive(False)
			self.qrcode_fullaccess.set_sensitive(False)
		else:
			version, size, image = qrencode.encode_scaled(
				'btsync://{0}?n={1}'.format(self.rwsecret,self.basename),232
			)
			self.rwqrcode = self.image_to_pixbuf(image)
			self.qrcode_image.set_from_pixbuf(self.rwqrcode)
			self.qrcode_fullaccess.set_active(True)

	def image_to_pixbuf(self,image):
		filebuf = StringIO()  
		image.save(filebuf, "ppm")  
		contents = filebuf.getvalue()  
		filebuf.close()  
		loader = GdkPixbuf.PixbufLoader.new_with_type("pnm")  
		#height, width = image.size
		#loader.set_size(width.height)
		loader.write(contents)  
		pixbuf = loader.get_pixbuf()  
		loader.close()  
		return pixbuf

	def onToggleFullAccess(self,widget):
		if widget.get_active():
			self.qrcode_image.set_from_pixbuf(self.rwqrcode)

	def onToggleReadOnly(self,widget):
		if widget.get_active():
			self.qrcode_image.set_from_pixbuf(self.roqrcode)


class BtSyncFolderPrefs(BtBaseDialog):
	def __init__(self,btsyncapi,secret):
		BtBaseDialog.__init__(self,
			'dialogs.glade',
			'folderprefs', [
				'rw_secret_text',
				'ro_secret_text',
				'ot_secret_text'
			]
		)
		result = btsyncapi.get_secrets(secret)
		self.rwsecret = result['read_write'] if result.has_key('read_write') else None
		self.rosecret = result['read_only']
		self.btsyncapi = btsyncapi
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

	def create(self):
		BtBaseDialog.create(self)
		# secrets page
		self.rw_secret = self.builder.get_object('rw_secret')
		self.rw_secret_text = self.builder.get_object('rw_secret_text')
		self.rw_secret_copy = self.builder.get_object('rw_secret_copy')
		self.rw_secret_new  = self.builder.get_object('rw_secret_new')
		self.ro_secret = self.builder.get_object('ro_secret')
		self.ro_secret_text = self.builder.get_object('ro_secret_text')
		self.ro_secret_copy = self.builder.get_object('ro_secret_copy')
		self.ot_secret = self.builder.get_object('ro_secret')
		self.ot_secret_text = self.builder.get_object('ot_secret_text')
		self.ot_secret_copy = self.builder.get_object('ot_secret_copy')
		self.ot_secret_new = self.builder.get_object('ot_secret_new')

		if self.rwsecret is None:
			self.rw_secret.set_sensitive(False)
			self.rw_secret_new.set_sensitive(False)
			self.rw_secret_copy.set_sensitive(False)
		else:
			self.rw_secret_text.set_text(str(self.rwsecret))

		self.ro_secret_text.set_text(str(self.rosecret))
		# prefs page

	def onRwSecretCopy(self,widget):
		text = self.rw_secret_text.get_text(*self.rw_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)

	def onRwSecretNew(self,widget):
		result = self.btsyncapi.get_secrets()
		self.rwsecret = result['read_write']
		self.rosecret = result['read_only']
		self.rw_secret_text.set_text(str(self.rwsecret))
		self.ro_secret_text.set_text(str(self.rosecret))

	def onRoSecretCopy(self,widget):
		text = self.ro_secret_text.get_text(*self.ro_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)


	def onOtSecretCopy(self,widget):
		text = self.ot_secret_text.get_text(*self.ot_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)


	def onOtSecretNew(self,widget):
		print "."

