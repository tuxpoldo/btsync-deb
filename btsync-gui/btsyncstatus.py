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
from btsyncapi import BtSyncApi

class BtSyncStatus(Gtk.StatusIcon):

	def __init__(self):
		Gtk.StatusIcon.__init__(self)
		self.set_name('btsync')
		self.set_title('BitTorrent Sync')
		self.set_tooltip_text('BitTorrent Sync Status Indicator')
		self.set_from_icon_name('btsync-gui-0')

		self.builder = Gtk.Builder()
		self.builder.add_from_file("btsyncstatus.glade")
		self.builder.connect_signals (self)
		self.menu = self.builder.get_object('btsyncmenu')
		self.about = self.builder.get_object('aboutdialog')

		self.connect('activate', self.onActivate)
		self.connect('popup-menu', self.onContextMenu)

		self.btsyncapi = BtSyncApi(port='9999')
		self.btsyncver = self.btsyncapi.get_version()

		# icon animator
		self.frame = 0
		self.rotating = False
		self.transferring = False


	def set_icon_rotating(self):
		self.frame = 0
		self.transferring = True
		if not self.rotating:
			GObject.timeout_add(200, self.onIconRotate)


	def onContextMenu(self,widget,button,activate_time):
		self.menu.popup(None,None,Gtk.StatusIcon.position_menu,widget,button,activate_time)

	def onActivate(self,widget):
		self.menu.popup(None,None,Gtk.StatusIcon.position_menu,widget,3,0)

	def onAbout(self,widget):
		self.about.set_version('Version {0} ({0})'.format(self.btsyncver['version']))
		self.about.show()
		self.about.run()
		self.about.hide()

	def onTogglePause(self,widget):
		print "onTogglePause"

	def onOpenApp(self,widget):
		print "onOpenApp"

	def onToggleLogging(self,widget):
		print "onToggleLogging"

	def onQuit(self,widget):
		Gtk.main_quit()

	def onIconRotate(self):
		if not self.transferring and self.frame % 12 == 0:
			# do not stop immediately - wait for the
			# cycle to finish.
			self.set_from_icon_name('btsync-gui-0')
			self.rotating = False
			self.frame = 0
			return False
		else:
			self.set_from_icon_name('btsync-gui-{0}'.format(self.frame % 12))
			self.rotating = True
			self.frame += 1
			return True


	def uptime(self):
		uptimef = open("/proc/uptime", "r")
		newupstr = uptimef.read()
		newuplst = newupstr.split()
		uptimef.close()
		return int(float(newuplst[0]) * 1000)

