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
import gettext
import qrencode
import requests

from gettext import gettext as _
from gi.repository import Gtk, Gdk, GdkPixbuf
from cStringIO import StringIO

from btsyncagent import BtSyncAgent
from btsyncutils import BtBaseDialog,BtInputHelper,BtValueDescriptor

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
			elif response == Gtk.ResponseType.DELETE_EVENT:
				return response
			elif response == Gtk.ResponseType.OK:
				self.secret = self.secret_w.get_text()
				self.folder = self.folder_w.get_text()
				# test if secret is OK
				if self.agent.get_error_code(self.agent.get_secrets(self.secret)) > 0:
					self.show_warning(_(
						'This secret is invalid.\nPlease generate a new '\
						'secret or enter your shared folder secret.'
					))
				# test if string is an absolute path and a directory
				elif len(self.folder) == 0 or self.folder[0] != '/' or not os.path.isdir(self.folder):
					self.show_warning(_('Can\'t open the destination folder.'))
				# test if the specified data is unique
				elif self.is_duplicate_folder(self.folder,self.secret):
					self.show_warning(_(
						'Selected folder is already added to BitTorrent Sync.'
					))
				# if btsync agent is local perform more tests
				elif self.agent.is_local():
					# test if the specified directory is readable and writable
					if not os.access(self.folder,os.W_OK) or not os.access(self.folder,os.R_OK):
						self.show_warning(_(
							'Don\'t have permissions to write to the selected folder.'
						))
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
		self.folderdlg = Gtk.FileChooserDialog (
			_('Please select a folder to sync'),
			self.dlg,
			Gtk.FileChooserAction.SELECT_FOLDER, (
				Gtk.STOCK_CANCEL,
				Gtk.ResponseType.CANCEL,
				Gtk.STOCK_OPEN,
				Gtk.ResponseType.OK
			)
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
	def __init__(self,agent):
		BtBaseDialog.__init__(self,
			'dialogs.glade',
			'folderprefs', [
				'fp_predefined_hosts',
				'rw_secret_text',
				'ro_secret_text',
				'en_secret_text',
				'ot_secret_text'
			]
		)
		self.agent = agent
		self.hostdlg = None
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

	def create(self,folder,secret):
		BtBaseDialog.create(self)
		# compute secrets
		result = self.agent.get_secrets(secret)
		self.idfolder = folder
		self.idsecret = secret
		self.rwsecret = result['read_write'] if result.has_key('read_write') else None
		self.rosecret = result['read_only'] if result.has_key('read_only') else None
		self.ensecret = result['encryption'] if result.has_key('encryption') else None
		# load values
		result = self.agent.get_folder_prefs(self.idsecret)
		# initialize OK button
		self.fp_button_ok = self.builder.get_object('fp_button_ok')
		# secrets page
		self.rw_secret = self.builder.get_object('rw_secret')
		self.rw_secret_text	= self.builder.get_object('rw_secret_text')
		self.rw_secret_copy	= self.builder.get_object('rw_secret_copy')
		self.rw_secret_new	= self.builder.get_object('rw_secret_new')

		self.ro_secret = self.builder.get_object('ro_secret')
		self.ro_secret_text = self.builder.get_object('ro_secret_text')
		self.ro_secret_copy = self.builder.get_object('ro_secret_copy')
		self.ro_restore	= self.builder.get_object('ro_restore')
		self.ro_restore_label	= self.builder.get_object('ro_restore_label')

		self.en_secret = self.builder.get_object('en_secret')
		self.en_secret_text = self.builder.get_object('en_secret_text')
		self.en_secret_copy = self.builder.get_object('en_secret_copy')

		self.ot_secret = self.builder.get_object('ot_secret')
		self.ot_secret_text = self.builder.get_object('ot_secret_text')
		self.ot_secret_copy = self.builder.get_object('ot_secret_copy')
		self.ot_secret_new	= self.builder.get_object('ot_secret_new')

		# secrets page - values
		self.ro_restore.set_active(self.agent.get_safe_result(result,'overwrite_changes',0) != 0)
		if self.ensecret is None:
			self.hide_en_secret()
		else:
			self.en_secret_text.set_text(str(self.ensecret))
		if self.rosecret is None:
			self.hide_ro_secret()
			self.hide_ot_secret()
			self.ro_restore.hide()
		else:
			self.ro_secret_text.set_text(str(self.rosecret))
		if self.rwsecret is None:
			self.hide_rw_secret()
		else:
			self.rw_secret_text.set_text(str(self.rwsecret))
			self.ro_restore.hide()
			self.ro_restore_label.hide()
		# prefs page
		self.fp_use_relay = self.builder.get_object('fp_use_relay')
		self.fp_use_tracker = self.builder.get_object('fp_use_tracker')
		self.fp_search_lan = self.builder.get_object('fp_search_lan')
		self.fp_use_dht = self.builder.get_object('fp_use_dht')
		self.fp_use_syncarchive = self.builder.get_object('fp_use_syncarchive')
		self.fp_use_predefined = self.builder.get_object('fp_use_predefined')
		self.fp_predefined_tree = self.builder.get_object('fp_predefined_tree')
		self.fp_predefined_hosts = self.builder.get_object('fp_predefined_hosts')
		self.fp_predefined_selection = self.builder.get_object('fp_predefined_selection')
		self.fp_predefined_add = self.builder.get_object('fp_predefined_add')
		self.fp_predefined_remove = self.builder.get_object('fp_predefined_remove')
		self.fp_predefined_label = self.builder.get_object('fp_predefined_label')
		# prefs page - values
		self.disable_hosts()
		self.fp_use_relay.set_active(self.agent.get_safe_result(result,'use_relay_server',0) != 0)
		self.fp_use_tracker.set_active(self.agent.get_safe_result(result,'use_tracker',0) != 0)
		self.fp_search_lan.set_active(self.agent.get_safe_result(result,'search_lan',0) != 0)
		self.fp_use_dht.set_active(self.agent.get_safe_result(result,'use_dht',0) != 0)
		self.fp_use_syncarchive.set_active(self.agent.get_safe_result(result,'use_sync_trash',0) != 0)
		self.fp_use_predefined.set_active(self.agent.get_safe_result(result,'use_hosts',0) != 0)
		# fill the list of predefined hosts...
		result = self.agent.get_folder_hosts(self.idsecret)
		if self.agent.get_error_code(result) == 0:
			hosts = result.get('hosts', [])
			for index, value in enumerate(hosts):
				self.fp_predefined_hosts.append ([ value ])

		# nothing is changed now
		self.fp_button_ok.set_sensitive(False)

	def response(self,result_id):
		if self.hostdlg is not None:
			self.hostdlg.response(result_id)
		BtBaseDialog.response(self,result_id)

	def hide_rw_secret(self):
		self.rw_secret.set_sensitive(False)
		self.rw_secret_new.set_sensitive(False)
		self.rw_secret_copy.set_sensitive(False)
		self.builder.get_object('rw_secret_label').hide()
		self.builder.get_object('rw_secret_scroll').hide()
		self.builder.get_object('rw_secret_box').hide()

	def hide_ro_secret(self):
		self.ro_secret.set_sensitive(False)
		self.ro_secret_copy.set_sensitive(False)
		self.builder.get_object('ro_secret_label').hide()
		self.builder.get_object('ro_secret_scroll').hide()
		self.builder.get_object('ro_secret_box').hide()

	def hide_en_secret(self):
		self.en_secret.set_sensitive(False)
		self.en_secret_copy.set_sensitive(False)
		self.builder.get_object('en_secret_label').hide()
		self.builder.get_object('en_secret_scroll').hide()
		self.builder.get_object('en_secret_box').hide()

	def show_en_secret(self):
		self.en_secret.set_sensitive(True)
		self.en_secret_copy.set_sensitive(True)
		self.builder.get_object('en_secret_label').show()
		self.builder.get_object('en_secret_scroll').show()
		self.builder.get_object('en_secret_box').show()

	def hide_ot_secret(self):
		self.ot_secret.set_sensitive(False)
		self.ot_secret_new.set_sensitive(False)
		self.ot_secret_copy.set_sensitive(False)
		self.builder.get_object('ot_secret_label').hide()
		self.builder.get_object('ot_secret_scroll').hide()
		self.builder.get_object('ot_secret_box').hide()
		self.builder.get_object('ot_secret_buttonbox').hide()
		self.builder.get_object('ot_secret_info').hide()

	def disable_hosts(self):
		self.fp_predefined_tree.set_sensitive(False)
		self.fp_predefined_add.set_sensitive(False)
		self.fp_predefined_remove.set_sensitive(False)
		self.fp_predefined_label.set_sensitive(False)

	def enable_hosts(self):
		self.fp_predefined_tree.set_sensitive(True)
		self.fp_predefined_add.set_sensitive(True)
		self.fp_predefined_remove.set_sensitive(self.fp_predefined_selection.count_selected_rows() > 0)
		self.fp_predefined_label.set_sensitive(True)

	def save_prefs(self):
		hosts_list = []
		for row in self.fp_predefined_hosts:
			hosts_list.append(row[0])
		self.agent.set_folder_hosts(self.idsecret,hosts_list)
		prefs = {}
		prefs['overwrite_changes'] = 1 if self.ro_restore.get_active() else 0
		prefs['use_relay_server'] = 1 if self.fp_use_relay.get_active() else 0
		prefs['use_tracker'] = 1 if self.fp_use_tracker.get_active() else 0
		prefs['search_lan'] = 1 if self.fp_search_lan.get_active() else 0
		prefs['use_dht'] = 1 if self.fp_use_dht.get_active() else 0
		prefs['use_sync_trash'] = 1 if self.fp_use_syncarchive.get_active() else 0
		prefs['use_hosts'] = 1 if self.fp_use_predefined.get_active() and len(hosts_list) > 0 else 0
		result = self.agent.set_folder_prefs(self.idsecret,prefs)
		return self.agent.get_error_code(result) == 0

	def onRwSecretCopy(self,widget):
		text = self.rw_secret_text.get_text(*self.rw_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)

	def onRwSecretNew(self,widget):
		result = self.agent.get_secrets()
		self.rw_secret_text.set_text(str(result['read_write']))
		# everything is now done by onSecretChanged
		# self.rwsecret = result['read_write']
		# self.rosecret = result['read_only']
		# self.rw_secret_text.set_text(str(self.rwsecret))
		# self.ro_secret_text.set_text(str(self.rosecret))

	def onRoSecretCopy(self,widget):
		text = self.ro_secret_text.get_text(*self.ro_secret_text.get_bounds(),include_hidden_chars=False)
		self.clipboard.set_text(text, -1)

	def onEnSecretCopy(self,widget):
		text = self.en_secret_text.get_text(*self.en_secret_text.get_bounds(),include_hidden_chars=False)
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
		if text != self.rwsecret:
			result = self.agent.get_secrets(text,throw_exceptions=False)
			if self.agent.get_error_code(result) == 0:
				if result.has_key('read_only'):
					self.ro_secret_text.set_text(str(result['read_only']))
				else:
					self.ro_secret_text.set_text('')
				if result.has_key('encryption'):
					self.show_en_secret()
					self.en_secret_text.set_text(str(result['encryption']))
				else:
					self.hide_en_secret()
					self.en_secret_text.set_text('')
				self.onChanged(None)

	def onPredefinedToggle(self,widget):
		self.onChanged(None)
		if widget.get_active():
			self.enable_hosts()
		else:
			self.disable_hosts()

	def onPredefinedSelectionChanged(self,selection):
		self.fp_predefined_remove.set_sensitive(selection.count_selected_rows() > 0)

	def onPredefinedAdd(self,widget):
		self.hostdlg = BtSyncHostAdd()
		self.hostdlg.create()
		if self.hostdlg.run() == Gtk.ResponseType.OK:
			self.fp_predefined_hosts.append ([ '{0}:{1}'.format(
				self.hostdlg.addr,
				self.hostdlg.port
			) ])
			self.onChanged(None)
		self.hostdlg.destroy()
		self.hostdlg = None

	def onPredefinedRemove(self,widget):
		model, tree_iter = self.fp_predefined_selection.get_selected()
		if tree_iter is not None:
			model.remove(tree_iter)
			self.onChanged(None)

	def onOK(self,widget):
		if self.rwsecret is not None:
			text = self.rw_secret_text.get_text(*self.rw_secret_text.get_bounds(),include_hidden_chars=False)
			if len(text) != 33 and len(text) < 40:
				self.show_error(_(
					'Invalid secret specified.\n'\
					'Secret must have a length of 33 characters'
				))
				self.dlg.response(0)
				return False
			result = self.agent.get_secrets(text,throw_exceptions=False)
			if self.agent.get_error_code(result) != 0:
				self.show_error(_(
					'Invalid secret specified.\n'\
					'Secret must contain only alphanumeric characters'
				))
				self.dlg.response(0)
				return False
			elif self.rwsecret != text:
				# the only way I know to change the secret is
				# to delete the folder and recreate it...
				# As we say in Germany: "Augen zu und durch!"
				# If we fail, we are f*****
				result = self.agent.remove_folder(self.rwsecret)
				result = self.agent.add_folder(self.idfolder,text)
				self.idsecret = text
				self.save_prefs()
				return True

		return self.save_prefs()

class BtSyncHostAdd(BtBaseDialog):
	def __init__(self):
		BtBaseDialog.__init__(self, 'dialogs.glade', 'newhost')
		self.addr = ''
		self.port = ''

	def create(self):
		BtBaseDialog.create(self)
		self.dlg.add_buttons(
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OK, Gtk.ResponseType.OK
		)
		self.addr_w = self.builder.get_object('ph_addr')
		self.port_w = self.builder.get_object('ph_port')

	def run(self):
		self.dlg.set_default_response(Gtk.ResponseType.OK)
		while True:
			response = BtBaseDialog.run(self)
			if response == Gtk.ResponseType.CANCEL:
				return response
			elif response == Gtk.ResponseType.DELETE_EVENT:
				return response
			elif response == Gtk.ResponseType.OK:
				self.addr = self.addr_w.get_text()
				self.port = self.port_w.get_text()
				# test if a hostname is specified
				if len(self.addr) == 0:
					self.show_warning(_(
						'A hostname or IP address must be specified'
					))
				# test if port is OK
				elif len(self.port) == 0 or int(self.port) < 1 or int(self.port) > 65534:
					self.show_warning(_(
						'The specified port must be a number between 1 and 65534'
					))
				else:
					return response

class BtSyncPrefsAdvanced(BtBaseDialog,BtInputHelper):

	def __init__(self,agent):
		BtBaseDialog.__init__(self,
			'dialogs.glade',
			'prefsadvanced', [
				'advancedprefs'
			]
		)
		BtInputHelper.__init__(self)
		self.agent = agent
		self.prefs = self.agent.get_prefs()
		self.create()

	def create(self):
		BtBaseDialog.create(self)
		# get the editing widgets
		self.advancedprefs = self.builder.get_object('advancedprefs')
		self.ap_tree_prefs = self.builder.get_object('ap_tree_prefs')
		self.ap_label_value = self.builder.get_object('ap_label_value')
		self.ap_switch_value = self.builder.get_object('ap_switch_value')
		self.ap_entry_value = self.builder.get_object('ap_entry_value')
		self.ap_reset_value = self.builder.get_object('ap_reset_value')
		# initialize content
		self.init_editor()
		self.init_values()

	def init_values(self):
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

	def init_editor(self,valDesc=None):
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
		self.init_editor(None if tree_iter is None else model[tree_iter][3])

	def onSaveEntry(self,widget,valDesc,newValue):
		try:
			self.agent.set_prefs({valDesc.Name : newValue})
			# GtkListStore has no search function. BAD!!! Maybe I'm too stupid?
			for row in self.advancedprefs:
				if row[0] == valDesc.Name:
					row[1] = str(newValue)
					row[2] = valDesc.get_display_width(newValue)
			return True
		except requests.exceptions.ConnectionError:
			return self.onConnectionError()
		except requests.exceptions.HTTPError:
			return self.onCommunicationError()

	def onPrefsAdvancedResetValue(self,widget):
		selection = self.ap_tree_prefs.get_selection()
		model, tree_iter = selection.get_selected()
		if tree_iter is not None:
			# reset to default
			valDesc = model[tree_iter][3]
			self.onSaveEntry(widget,valDesc,valDesc.Default)
			valDesc.set_default()
			self.init_editor(valDesc)

	def onConnectionError(self):
		self.response(Gtk.ResponseType.CANCEL)
		self.dlg.destroy()

	def onCommunicationError(self):
		self.response(Gtk.ResponseType.CANCEL)
		self.dlg.destroy()


