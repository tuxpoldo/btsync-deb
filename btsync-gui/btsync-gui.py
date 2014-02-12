#!/usr/bin/env python

from gi.repository import Gtk, Gdk
from btsyncapi import BtSyncApi

class BtSyncApp:

	def __init__(self):
		self.btsyncapi = BtSyncApi(port='9999')
		self.builder = Gtk.Builder()
		self.builder.add_from_file("btsync-gui.glade")
		self.builder.connect_signals (self)
		self.window = self.builder.get_object('mainwindow')
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
		self.preferences_locked = True
		self.devname.set_text(self.prefs["device_name"])
		# self.autostart.set_active(self.prefs[""]);
		self.listeningport.set_text(str(self.prefs["listening_port"]))
		self.upnp.set_active(self.prefs["use_upnp"] != 0)
		self.limitdn.set_active(self.prefs["download_limit"] > 0)
		self.limitdnrate.set_text(str(self.prefs["download_limit"]));
		self.limitup.set_active(self.prefs["upload_limit"] > 0)
		self.limituprate.set_text(str(self.prefs["upload_limit"]));
		self.preferences_locked = False

	def onPreferencesChangedDeviceName(self,widget):
		self.handleChangedTextEntry(widget,'device_name')

	def onPreferencesSaveDeviceName(self,widget,iconposition,event):
		self.handleSaveTextEntry(widget,iconposition,'device_name')

	def onPreferencesChangedListeningPort(self,widget):
		self.handleChangedNumberEntry(widget,'listening_port',minval=1025,maxval=65534)

	def onPreferencesSaveListeningPort(self,widget,iconposition,event):
		self.handleSaveNumberEntry(widget,iconposition,'listening_port',minval=1025,maxval=65534)

	def onPreferencesChangedDownloadRate(self,widget):
		self.handleChangedNumberEntry(widget,'download_limit',maxval=1000000)

	def onPreferencesSaveDownloadRate(self,widget,iconposition,event):
		self.handleSaveNumberEntry(widget,iconposition,'download_limit',maxval=1000000)

	def onPreferencesChangedUploadRate(self,widget):
		self.handleChangedNumberEntry(widget,'upload_limit')

	def onPreferencesSaveUploadRate(self,widget,iconposition,event):
		self.handleSaveNumberEntry(widget,iconposition,'upload_limit',maxval=1000000)

	def onPreferencesUPnPToggled(self,widget):
		self.handleChangedToggle(widget,'use_pnp')

	def onPreferencesLimitDnToggled(self,widget):
		self.limitdnrate.set_sensitive(widget.get_active())
		if not self.preferences_locked:
			rate = int(self.limitdnrate.get_text()) if widget.get_active() else 0
			self.btsyncapi.set_prefs({"download_limit" : rate})

	def onPreferencesLimitUpToggled(self,widget):
		self.limituprate.set_sensitive(widget.get_active())
		if not self.preferences_locked:
			rate = int(self.limituprate.get_text()) if widget.get_active() else 0
			self.btsyncapi.set_prefs({"upload_limit" : rate})

	def onChangedPredefinedHosts(self, *args):
		a = 1

	def onNewFaSecret(self, *args):
		a = 1

	def onCopyFaSecret(self, *args):
		a = 1

	def onCopyRoSecret(self, *args):
		a = 1

	def onNewOtSecret(self, *args):
		a = 1

	def onChangedPredefinedHosts(self, *args):
		a = 1

	def handleChangedNumberEntry(self,widget,key,default=0,minval=None,maxval=None):
		if not self.preferences_locked:
			self.filterNumbers(widget,default,minval,maxval)
			self.handleChangedEntry(widget,key)

	def handleSaveNumberEntry(self,widget,iconposition,key,default=0,minval=None,maxval=None):
		if not self.preferences_locked and iconposition == Gtk.EntryIconPosition.SECONDARY:
			self.filterNumbers(widget,default,minval,maxval)
			value = int(widget.get_text())
			self.btsyncapi.set_prefs({key : value})
			self.prefs[key] = value
			widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)

	def handleChangedTextEntry(self,widget,key,default='',forbidden='\'"'):
		if not self.preferences_locked:
			self.filterText(widget,default,forbidden)
			self.handleChangedEntry(widget,key)

	def handleSaveTextEntry(self,widget,iconposition,key,default='',forbidden='\'"'):
		if not self.preferences_locked and iconposition == Gtk.EntryIconPosition.SECONDARY:
			self.filterText(widget,default,forbidden)
			value = widget.get_text()
			self.btsyncapi.set_prefs({key : value})
			self.prefs[key] = value
			widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)

	def handleChangedToggle(self,widget,key):
		if not self.preferences_locked:
			value = 1 if widget.get_active() else 0
			self.btsyncapi.set_prefs({key : value})
			self.prefs[key] = value

	def handleChangedEntry(self,widget,key):
		if widget.get_text() != str(self.prefs[key]):
			widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, 'gtk-save')
		else:
			widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)
		
	def filterNumbers(self,widget,default=0,minval=None,maxval=None):
		value = widget.get_text()
		if not value.isdigit():
			mask = value.strip('0123456789')
			value = value.strip(mask)
			if value is '':
				value = str(default)
			widget.set_text(value)
		if minval is not None and int(value) < minval:
			value = str(minval)
			widget.set_text(value)
		elif maxval is not None and int(value) > maxval:
			value = str(maxval)
			widget.set_text(value)

	def filterText(self,widget,default='',forbidden='\'"'):
		value = widget.get_text()
		newvalue = value.strip(forbidden)
		if newvalue is '':
			newvalue = str(default)
		if newvalue != value:
			widget.set_text(newvalue)




if __name__ == "__main__":
	app = BtSyncApp()
	Gtk.main()
