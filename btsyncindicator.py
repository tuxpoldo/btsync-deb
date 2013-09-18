#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 Mark Johnson
#
# Authors: Mark Johnson
#
# Based on the PyGTK Application Indicators example by Jono Bacon
# and Neil Jagdish Patel
# http://developer.ubuntu.com/resources/technologies/application-indicators/
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
import gobject
import gtk
import appindicator

import urllib
import requests
import time
import sys
import re
import json
import os
import argparse
import webbrowser

VERSION = '0.6'
TIMEOUT = 2 # seconds

class BtSyncIndicator:
    def __init__(self):
        """
        Initialise the indicator, load the config file,
        intialise some properties and set up the basic
        menu
        """

        self.ind = appindicator.Indicator ("btsync-indicator",
                                          "btsync",
                                          appindicator.CATEGORY_APPLICATION_STATUS,
                                          args.iconpath)
        self.ind.set_status (appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon ("btsync-attention")

        self.load_config()

        self.urlroot = 'http://'+self.config['webui']['listen']+'/gui/'
        self.folderitems = {}
        self.info = {}
        self.clipboard = gtk.Clipboard()
        self.animate = None
        self.error_item = None
        self.frame = 0

        self.menu_setup()
        self.ind.set_menu(self.menu)

    def load_config(self):
        """
        Open the config file specified in args load into self.config
        """
        config = ""
        for line in open(args.config, 'r'):
            if line.find('//') == -1:
                config += line
        self.config = json.loads(config)

    def menu_setup(self):
        """
        Create the menu with some basic items
        """
        # create a menu
        self.menu = gtk.Menu()

	self.webui_item = gtk.MenuItem("Open Web Interface")
	self.webui_item.connect("activate", self.open_webui)
	self.webui_item.show()
	self.menu.append(self.webui_item)
                    
        sep = gtk.SeparatorMenuItem()
        sep.show()
        self.menu.append(sep)

	self.debug_item = gtk.CheckMenuItem("Enable Debug Logging")
	self.debug_item.connect("activate", self.toggle_debugging)
	self.debug_item.show()
	self.menu.append(self.debug_item)

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def setup_session(self):
        """
        Attempt to setup the session with the btsync server
        * Calls token.html, stores the token and cookie
        * Calls various actions called by the web interface on init and stores results
        * Initialises check_status loop
        If the server cannot be contacted, waits 5 seconds and retries.
        """
        try:
            tokenparams = {'t': time.time()}
            tokenurl = self.urlroot+'token.html'
            tokenresponse = requests.post(tokenurl, params=tokenparams)
            regex = re.compile("<html><div[^>]+>([^<]+)</div></html>")
            html = self.get_response_text(tokenresponse)
            r = regex.search(html)
            self.token = r.group(1)
            self.cookies = tokenresponse.cookies

            actions = [
                  'license', 
                  'getostype', 
                  'getsettings', 
                  'getversion', 
                  'getdir', 
                  'checknewversion', 
                  'getuserlang', 
                  'iswebuilanguageset']


            for a in actions:
               params = {'token': self.token, 'action': a}
               response = requests.get(self.urlroot, params=params, cookies=self.cookies)
               self.info[a] = json.loads(self.get_response_text(response))

            self.clear_error()

            gtk.timeout_add(TIMEOUT * 1000, self.check_status)
            return False

        except requests.exceptions.ConnectionError:
            self.show_error("Couldn't connect to Bittorrent Sync at "+self.urlroot)
            return True

    def check_status(self):
        """
        Gets the current status of btsync and updates the menu accordingly
        Shows each shared folder with connected peer and any transfer activity 
        with it.  Also retrieves the secrets for each folder.
        If the server cannot be contacted, stops polling and attempts calls setup_session
        to establish a new session.
        """
        try:
            params = {'token': self.token, 'action': 'getsyncfolders'}
            response = requests.get(self.urlroot, params=params, cookies=self.cookies)

            self.clear_error()

            status = json.loads(self.get_response_text(response))

            self.check_activity(status['folders'])

            for folder in status['folders']:
                name = folder['name']
                buf = name+" "+folder['size']
                if name in self.folderitems:
                    folderitem = self.folderitems[name]
                    menuitem = folderitem['menuitem']
                    buf = menuitem.set_label(buf)
                else:
                    menuitem = gtk.MenuItem(buf)
                    self.menu.prepend(menuitem)
                    menuitem.show()
                    menuitem.set_sensitive(False)
                    folderitem = {'menuitem': menuitem, 'peeritems': {}}
                    self.folderitems[name] = folderitem

                    pos = self.menu.get_children().index(menuitem)

                    buf = "Get Secret"
                    secretitem = gtk.MenuItem(buf)
                    secretmenu = self.build_secret_menu(folder)
                    secretitem.set_submenu(secretmenu)
                    self.menu.insert(secretitem, pos+1)
                    secretitem.show()

                    sep = gtk.SeparatorMenuItem()
                    self.menu.insert(sep, pos+2)
                    sep.show()

                if len(folder['peers']) > 0:
                    for peer in folder['peers']:
                        if peer['name'] in folderitem['peeritems']:
                            self.update_peer(folderitem['peeritems'][peer['name']], peer)
                        else:
                            self.add_peer(folderitem, peer)
                else:
                    if len(folderitem['peeritems']) > 0:
                        for peeritem in folderitem['peeritems']:
                            self.remove_peer(folderitem, peeritem)

        except requests.exceptions.ConnectionError:
            self.show_error("Lost connection to Bittorrent Sync")
            self.folderitems = {}
            gtk.timeout_add(5000, self.setup_session)

        return True;

    def check_activity(self, folders):
        """
        Given the current folder list from the server, determines
        whether there is any network activity and sets a flag in
        self.active
        """
        isactive = False
        for folder in folders:
            for peer in folder['peers']:
                if peer['status'].find('Synced') == -1:
                    isactive = True
                    break

        self.active = isactive
        if self.active:
            if self.animate == None:
                gtk.timeout_add(1000, self.animate_icon)




    def add_peer(self, folderitem, peer):
        """
        Adds a peer with the specified data below the specified menu
        item.
        """
	name = peer['name']
        buf = self.format_status(peer)
        peeritem = gtk.MenuItem(buf)
	folderposition = self.menu.get_children().index(folderitem['menuitem'])
	self.menu.insert(peeritem, folderposition+1)
	peeritem.set_sensitive(False)
	peeritem.show()
	folderitem['peeritems'][name] = peeritem
        return True;

    def update_peer(self, peeritem, peer):
        """
        Updates the specified menu item with the peer information provided
        """
        buf = self.format_status(peer)
        peeritem.set_label(buf)
        return True;

    def remove_peer(self, folderitem, peeritem):
        """
        Removes the peer item below the folder item
        """
        self.menu.remove(peer)
        del folderitem['peeritems'][peeritem]
        return True;

    def format_status(self, peer):
        """
        Formats the peer status information for display.
        Substitues HTML tags with appropriate unicode characters and 
        returns name followed by status.
        """
	name = peer['name']
	status = peer['status'].replace("<div class='uparrow' />", "⇧")
	status = status.replace("<div class='downarrow' />", "⇩")
        return name+': '+status

    def build_secret_menu(self, folder):
        """
        Builds and returns submenu for copying secrets of the given folder
        to the clipboard
        """
	menu = gtk.Menu()
	readonly = gtk.MenuItem('Read only')
	readonly.connect("activate", self.copy_secret, folder['readonlysecret'])
	readwrite = gtk.MenuItem('Full access')
	readwrite.connect("activate", self.copy_secret, folder['secret'])
	menu.append(readonly)
	menu.append(readwrite)
	readonly.show()
	readwrite.show()
	return menu

    def show_error(self, message):
        """
        Removes all items from the menu (except quit) and displays an error
        message in their place. Also changes the icon to an error icon.
        """
        self.active = False
        if self.error_item == None:                    
            self.set_icon('-error')

            for child in self.menu.get_children():
                if child != self.quit_item:
                    self.menu.remove(child)

            self.error_item = gtk.MenuItem(message)
            self.error_item.set_sensitive(False)
            self.menu.prepend(self.error_item)
            self.error_item.show()

    def clear_error(self):
        """
        Removes the error message from the menu and changes the icon back
        to normal
        """
        if self.error_item != None:
            self.menu.remove(self.error_item)
            self.error_item = None
            self.set_icon('')

    def copy_secret(self, menuitem, secret):
        """
        Copies the supplied secret to the clipboard
        """
    	self.clipboard.set_text(secret)
    	return True;

    def animate_icon(self):
        """
        Cycles the icon through 3 frames to indicate network activity
        """
        if self.active == False:
            self.animate = None
            self.set_icon('')
            self.frame = 0
            return False
        else:
            self.animate = True
            self.set_icon('-active-{}'.format(self.frame % 3))
            self.frame += 1
            return True
        
    def set_icon(self, variant):
        """
        Changes the icon to the given variant
        """
        self.ind.set_icon('btsync'+variant)
        return False

    def open_webui(self, widget):
        """
        Opens a browser to the address of the WebUI indicated in the config file
        """
	webbrowser.open('http://'+self.config['webui']['listen'], 2)
	return True

    def toggle_debugging(self, widget):
        """
        Creates or clears the debugging flags for btsync
        """
	filepath = self.config['storage_path']+'/debug.txt'
	if (os.path.isfile(filepath)):
	    os.unlink(filepath)
	else:
	    f = open(filepath, 'w')
	    f.write('FFFF')
	return True

    def get_response_text(self, response):
        """
        Version-safe way to get the response text from a requests module response object
        Older versions use response.content instead of response.text
        """
        return response.text if hasattr(response, "text") else response.content

    def main(self):
        gtk.timeout_add(TIMEOUT * 1000, self.setup_session)
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', 
                        default=os.environ['HOME']+'/.btsync.conf',
                        help="Location of Bittorrent Sync config file")
    parser.add_argument('--iconpath', 
                        default=os.path.dirname(os.path.realpath(__file__))+"/icons",
                        help="Path to icon theme folder")
    parser.add_argument('-v', '--version',
			action='store_true',
                        help="Print version information and exit")
    args = parser.parse_args()

    if (args.version):
	print os.path.basename(__file__)+" Version "+VERSION;
	exit()

    indicator = BtSyncIndicator()
    indicator.main()
