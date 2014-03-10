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
import qrencode

from gi.repository import Gtk, Gdk, GdkPixbuf
from cStringIO import StringIO
from btsyncagent import BtSyncAgent
from btsyncutils import BtBaseDialog

class BtSyncFolderRemove(BtBaseDialog):
	def __init__(self):
		BtBaseDialog.__init__(self, 'dialogs.glade', 'removefolder')

class BtSyncFolderAdd(BtBaseDialog):
	def __init__(self,agent):
		BtBaseDialog.__init__(self, 'dialogs.glade', 'addfolder')
		self.folderdlg = None
		self.agent = agent
		self.secret = ''
		self.folder = ''

	def create(self):
		BtBaseDialog.create(self)
		self.secret_w = self.builder.get_object('addfolder_secret')
		self.folder_w = self.builder.get_object('addfolder_folder')
		self.choose_b = self.builder.get_object('addfolder_choose')
		self.choose_b.set_sensitive(self.agent.is_local())

	def run(self):
		while True:
			response = BtBaseDialog.run(self)
			if response == Gtk.ResponseType.CANCEL:
				return response
			elif response == Gtk.ResponseType.OK:
				self.secret = self.secret_w.get_text()
				self.folder = self.folder_w.get_text()
				# test if secret is OK
				if self.agent.get_error_code(self.agent.get_secrets(self.secret)) > 0:
					self.show_warning(
						'This secret is invalid.\nPlease generate a new '\
						'secret or enter your shared folder secret.'
					)
				# test if string is an absolute path and a directory
				elif len(self.folder) == 0 or self.folder[0] != '/' or not os.path.isdir(self.folder):
					self.show_warning('Can\'t open the destination folder.')
				# test if the specified data is unique
				elif self.is_duplicate_folder(self.folder,self.secret):
					self.show_warning('Selected folder is already added to BitTorrent Sync.')
				# if btsync agent is local perform more tests
				elif self.agent.is_local():
					# test if the specified directory is readable and writable
					if not os.access(self.folder,os.W_OK) or not os.access(self.folder,os.R_OK):
						self.show_warning(
							'Don\'t have permissions to write to the selected folder.'
						)
					else:
						return response
				else:
					return response

	def response(self,result_id):
		if self.folderdlg is not None:
			self.folderdlg.response(result_id)
		BtBaseDialog.response(self,result_id)

	def is_duplicate_folder(self,folder,secret):
		folders = self.agent.get_folders()
		if folders is not None:
			for index, value in enumerate(folders):
				if value['dir'] == folder or value['secret'] == secret:
					return True
		return False;


	def onFolderAddChoose(self,widget):
		self.folderdlg = Gtk.FileChooserDialog ("Please select a folder to sync", self.dlg,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		)
		if self.folderdlg.run() == Gtk.ResponseType.OK:
			self.folder_w.set_text(self.folderdlg.get_filename())
		self.folderdlg.destroy()
		self.folderdlg = None

	def onFolderAddGenerate(self,widget):
		secrets = self.agent.get_secrets()
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
	def __init__(self,api):
		BtBaseDialog.__init__(self,
			'dialogs.glade',
			'folderprefs', [
				'rw_secret_text',
				'ro_secret_text',
				'ot_secret_text'
			]
		)
		self.api = api
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

	def create(self,folder,secret):
		BtBaseDialog.create(self)
		# compute secrets
		result = self.api.get_secrets(secret)
		self.idfolder = folder
		self.idsecret = secret
		self.rwsecret = result['read_write'] if result.has_key('read_write') else None
		self.rosecret = result['read_only']
		# initialize OK button
		self.fp_button_ok = self.builder.get_object('fp_button_ok')
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
		# secrets page - values
		if self.rwsecret is None:
			self.rw_secret.set_sensitive(False)
			self.rw_secret_new.set_sensitive(False)
			self.rw_secret_copy.set_sensitive(False)
		else:
			self.rw_secret_text.set_text(str(self.rwsecret))
		self.ro_secret_text.set_text(str(self.rosecret))
		# prefs page
		self.fp_use_relay = self.builder.get_object('fp_use_relay')
		self.fp_use_tracker = self.builder.get_object('fp_use_tracker')
		self.fp_search_lan = self.builder.get_object('fp_search_lan')
		self.fp_use_dht = self.builder.get_object('fp_use_dht')
		self.fp_use_syncarchive = self.builder.get_object('fp_use_syncarchive')
		self.fp_use_predefined = self.builder.get_object('fp_use_predefined')
		self.fp_predefined_tree = self.builder.get_object('fp_predefined_tree')
		self.fp_predefined_add = self.builder.get_object('fp_predefined_add')
		self.fp_predefined_remove = self.builder.get_object('fp_predefined_remove')
		self.fp_predefined_label = self.builder.get_object('fp_predefined_label')
		# prefs page - values
		result = self.api.get_folder_prefs(self.idsecret)
		self.fp_use_relay.set_active(self.api.get_safe_result(result,'use_relay_server',0) != 0)
		self.fp_use_tracker.set_active(self.api.get_safe_result(result,'use_tracker',0) != 0)
		self.fp_search_lan.set_active(self.api.get_safe_result(result,'search_lan',0) != 0)
		self.fp_use_dht.set_active(self.api.get_safe_result(result,'use_dht',0) != 0)
		self.fp_use_syncarchive.set_active(self.api.get_safe_result(result,'use_sync_trash',0) != 0)
		self.fp_use_predefined.set_active(self.api.get_safe_result(result,'use_hosts',0) != 0)
		self.fp_use_predefined.set_sensitive(False)
		self.fp_predefined_tree.set_sensitive(False)
		self.fp_predefined_add.set_sensitive(False)
		self.fp_predefined_remove.set_sensitive(False)
		self.fp_predefined_label.set_sensitive(False)
		# nothing is changed now
		self.fp_button_ok.set_sensitive(False)

	def save_prefs(self):
		prefs = {}
		prefs['use_relay_server'] = 1 if self.fp_use_relay.get_active() else 0
		prefs['use_tracker'] = 1 if self.fp_use_tracker.get_active() else 0
		prefs['search_lan'] = 1 if self.fp_search_lan.get_active() else 0
		prefs['use_dht'] = 1 if self.fp_use_dht.get_active() else 0
		prefs['use_sync_trash'] = 1 if self.fp_use_syncarchive.get_active() else 0
		result = self.api.set_folder_prefs(self.idsecret,prefs)
		return self.api.get_error_code(result) == 0

	def onRwSecretCopy(self,widget):
		text = self.rw_secret_text.get_text(*self.rw_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)

	def onRwSecretNew(self,widget):
		result = self.api.get_secrets()
		self.rw_secret_text.set_text(str(result['read_write']))
		# everything is done by onCHangeSecret
		# self.rwsecret = result['read_write']
		# self.rosecret = result['read_only']
		# self.rw_secret_text.set_text(str(self.rwsecret))
		# self.ro_secret_text.set_text(str(self.rosecret))

	def onRoSecretCopy(self,widget):
		text = self.ro_secret_text.get_text(*self.ro_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)


	def onOtSecretCopy(self,widget):
		text = self.ot_secret_text.get_text(*self.ot_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)

	def onOtSecretNew(self,widget):
		# not implemented
		pass

	def onChanged(self,widget):
		self.fp_button_ok.set_sensitive(True)

	def onSecretChanged(self,textbuffer):
		text = self.rw_secret_text.get_text(*self.rw_secret_text.get_bounds(),include_hidden_chars=False)
		if len(text) == 33:
			if text != self.rwsecret:
				result = self.api.get_secrets(text,throw_exceptions=False)
				if self.api.get_error_code(result) == 0:
					self.ro_secret_text.set_text(str(result['read_only']))
					self.onChanged(None)

	def onOK(self,widget):
		if self.rwsecret is not None:
			text = self.rw_secret_text.get_text(*self.rw_secret_text.get_bounds(),include_hidden_chars=False)
			if len(text) != 33:
				self.show_error(
					'Invalid secret specified.\n'\
					'Secret must have a length of 33 characters'
				)
				self.dlg.response(0)
				return False
			elif not text.isalnum():
				self.show_error(
					'Invalid secret specified.\n'\
					'Secret must contain only alphanumeric characters'
				)
				self.dlg.response(0)
				return False
			elif self.rwsecret != text:
				# the only way I know to change the secret is
				# to delete the folder and recreate it...
				# As we say in Germany: "Augen zu und durch!"
				# If we fail, we are f*****
				result = self.api.remove_folder(self.rwsecret)
				result = self.api.add_folder(self.idfolder,text)
				self.idsecret = text
				self.save_prefs()
				return True

		return self.save_prefs()

