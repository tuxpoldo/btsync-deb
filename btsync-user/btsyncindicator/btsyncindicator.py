#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 Mark Johnson
#
# Authors: Mark Johnson and Contributors (see CREDITS)
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

"""
    Requests is not installed by default
    If it's missing, display instructions to install with apt or pip
"""
try:
    import requests
except ImportError:
    print "requests library not found."
    print "To install, try:"
    print "sudo apt-get install python-requests"
    print "If python-requests isn't found, try:"
    print "sudo apt-get install python-pip && sudo pip install requests"
    print "If apt-get isn't available, use your system's package manager or install pip manually:"
    print "http://www.pip-installer.org/en/latest/installing.html"
    exit(1)

import time
import sys
import re
import json
import os
import argparse
import webbrowser
import logging
import subprocess
from contextlib import contextmanager

VERSION = '0.16'
TIMEOUT = 2 # seconds

@contextmanager
def file_lock(lock_file):
    runningpids = subprocess.check_output("ps aux | grep btsyncindicator | grep -v grep | awk '{print $2}'", shell=True).split()
    if os.path.exists(lock_file):
        # is it a zombie?
        f = open(lock_file, 'r')
        pid = f.read()
        f.close()
        if pid not in runningpids:
            os.remove(lock_file)
        else:
            print 'Only one indicator can run at once. '\
                  'Indicator is locked with %s' % lock_file
            sys.exit(-1)

    open(lock_file, 'w').write(str(os.getpid()))
    try:
        yield
    finally:
        os.remove(lock_file)


class BtSyncConfig:
    def __init__(self):
        self.load_config()

    def load_config(self):
        """
        Open the config file specified in args load into self.config
	Removes commented lines starting in //, or multi-line comments
	wrapped in /* */
        """
        logging.info('Opening config file '+args.config)
        config = ""
        for line in open(args.config, 'r'):
            if line.find('//') == -1:
                config += line
        config = re.sub("/\*(.|[\r\n])*?\*/", "", config)
        self.config = json.loads(config)
        logging.info('Config loaded')


class BtSyncIndicator:
    def __init__(self,btconf):
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

        self.config = btconf.config
        self.detect_btsync_user()
        
        if 'login' in self.config['webui']:
            login = self.config['webui']['login']
            password = self.config['webui']['password']
            self.webui = 'http://'+login+':'+password+'@'+self.config['webui']['listen'] if self.btsync_user else 'http://'+self.config['webui']['listen']
            self.auth = (login, password)
        else:
            self.webui = 'http://'+self.config['webui']['listen']
            self.auth = None

        self.urlroot = 'http://'+self.config['webui']['listen']+'/gui/'
        self.folderitems = {}
        self.info = {}
        self.clipboard = gtk.Clipboard()
        self.animate = None
        self.error_item = None
        self.frame = 0
        self.status = None
        self.count = 0

        self.menu_setup()
        self.ind.set_menu(self.menu)

    def detect_btsync_user(self):
        # If we have dpkg in $PATH, Determine whether the script was installed with 
	# the btsync-user package if it is, we can use the packages btsync management
	# scripts for some extra features
        try:
            have_dpkg = False
            for p in os.environ["PATH"].split(os.pathsep):
                if os.path.exists(os.path.join(p, 'dpkg')):
                    have_dpkg = True

            if have_dpkg:
                output = subprocess.check_output(["dpkg", "-S", os.path.abspath(__file__)])
            else:
                output = ""

            if (output.find("btsync-user") > -1):
                self.btsync_user = True
            else:
                self.btsync_user = False
        except subprocess.CalledProcessError, e:
            self.btsync_user = False
        return self.btsync_user

    def menu_setup(self):
        """
        Create the menu with some basic items
        """
        logging.info('Creating menu')
        # create a menu
        self.menu = gtk.Menu()

        self.sep1 = gtk.SeparatorMenuItem()
        self.sep1.show()
        self.menu.append(self.sep1)

        if self.btsync_user:
            filepath = self.config['storage_path']+'/paused'
            self.pause_item = gtk.CheckMenuItem("Pause Syncing")
            self.pause_item.set_active(os.path.isfile(filepath))
            self.pause_item_handler = self.pause_item.connect("activate", self.toggle_pause)
            self.pause_item.show()
            self.menu.append(self.pause_item)

	self.webui_item = gtk.MenuItem("Open Web Interface")
	self.webui_item.connect("activate", self.open_webui)
	self.webui_item.show()
	self.menu.append(self.webui_item)
                    
        self.sep2 = gtk.SeparatorMenuItem()
        self.sep2.show()
        self.menu.append(self.sep2)

        filepath = self.config['storage_path']+'/debug.txt'
	self.debug_item = gtk.CheckMenuItem("Enable Debug Logging")
	self.debug_item.set_active(os.path.isfile(filepath))
	self.debug_item_handler = self.debug_item.connect("activate", self.toggle_debugging)
	self.debug_item.show()
	self.menu.append(self.debug_item)

        if self.btsync_user:
            buf = "Quit BitTorrent Sync"
        else:
            buf = "Quit"
        self.quit_item = gtk.MenuItem(buf)
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)
        logging.info('Menu initalisation complete')

    def setup_session(self):
        """
        Attempt to setup the session with the btsync server
        * Calls token.html, stores the token and cookie
        * Calls various actions called by the web interface on init and stores results
        * Initialises check_status loop
        If the server cannot be contacted, waits 5 seconds and retries.
        """
        if self.btsync_user:
            filepath = self.config['storage_path']+'/paused'
            if (os.path.isfile(filepath)):
                logging.info('BitTorrent Sync is paused. Skipping session setup')
                self.show_error("BitTorrent Sync is paused")
                return True

        try:
            tokenparams = {'t': time.time()}
            tokenurl = self.urlroot+'token.html'
            logging.info('Requesting Token from ' + tokenurl)
            response = requests.post(tokenurl, params=tokenparams, auth=self.auth)
            response.raise_for_status()
            logging.info('Token response ' + str(response))
            regex = re.compile("<html><div[^>]+>([^<]+)</div></html>")
            html = self.get_response_text(response)
            logging.info('HTML Response ' + html)
            r = regex.search(html)
            self.token = r.group(1)
            self.cookies = response.cookies
            logging.info('Token '+self.token+' Retrieved')

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
               response = requests.get(self.urlroot, params=params, cookies=self.cookies, auth=self.auth)
               response.raise_for_status()
               self.info[a] = self.get_response_json(response)

            self.clear_error()

            logging.info('Session setup complete, initialising check_status loop')

            self.status = { 'folders': [] }

            gtk.timeout_add(TIMEOUT * 1000, self.check_status)
            return False

        except requests.exceptions.ConnectionError:
            logging.warning('Connection Error caught, displaying error message')
            self.show_error("Couldn't connect to Bittorrent Sync at "+self.urlroot)
            return True
        except requests.exceptions.HTTPError:
            logging.warning('Communication Error caught, displaying error message')
            self.show_error("Communication Error "+str(response.status_code))
            return True

    def check_status(self):
        """
        Gets the current status of btsync and updates the menu accordingly
        Shows each shared folder with connected peer and any transfer activity 
        with it.  Also retrieves the secrets for each folder.
        If the server cannot be contacted, stops polling and attempts calls setup_session
        to establish a new session.
        """
        """
        Since some state information from the btsync-agent may be changed from outside,
        we should keep it also up to date in the menu...
        """
        filepath = self.config['storage_path']+'/debug.txt'
        self.debug_item.disconnect(self.debug_item_handler)
	self.debug_item.set_active(os.path.isfile(filepath))
	self.debug_item_handler = self.debug_item.connect("activate", self.toggle_debugging)

	if self.btsync_user:
            filepath = self.config['storage_path']+'/paused'
            self.pause_item.disconnect(self.pause_item_handler)
            self.pause_item.set_active(os.path.isfile(filepath))
            self.pause_item_handler = self.pause_item.connect("activate", self.toggle_pause)
            if (os.path.isfile(filepath)):
                logging.info('BitTorrent Sync is paused. Cleaning menu')
                self.show_error("BitTorrent Sync is paused")
                self.folderitems = {}
                self.status = { 'folders': [] }
                gtk.timeout_add(5000, self.setup_session)
                return False

        try:
            logging.info('Requesting status')
            params = {'token': self.token, 'action': 'getsyncfolders'}
            response = requests.get(self.urlroot, params=params, cookies=self.cookies, auth=self.auth)
            response.raise_for_status()

            self.clear_error()

            status = self.get_response_json(response)

            self.check_activity(status['folders'])

            curfoldernames = [ folder['name'] for folder in self.status['folders'] ]
            newfoldernames = [ folder['name'] for folder in status['folders'] ]

            updatefolders = [ folder for folder in status['folders'] if folder['name'] in curfoldernames ]
            newfolders = [ folder for folder in status['folders'] if folder['name'] not in curfoldernames ]
            oldfolders = [ folder for folder in self.status['folders'] if folder['name'] not in newfoldernames ]
            
            for folder in newfolders:
                name = folder['name']
                menuitem = gtk.MenuItem(name)
                self.menu.prepend(menuitem)
                menuitem.show()
                folderitem = {'menuitem': menuitem, 'sizeitem': {}, 'peeritems': {}}
                self.folderitems[name] = folderitem
                submenu = self.build_folder_menu(folder)
                menuitem.set_submenu(submenu)

            for folder in updatefolders:
                self.update_folder_menu(folder)

            for folder in oldfolders:
                name = folder['name']
                self.menu.remove(self.folderitems[name]['menuitem'])
                del self.folderitems[name]

            self.status = status
            return True

        except requests.exceptions.ConnectionError:
            logging.warning('Status request failed, attempting to re-initialise session')
            self.show_error("Lost connection to Bittorrent Sync")
            self.folderitems = {}
            self.status = { 'folders': [] }
            gtk.timeout_add(5000, self.setup_session)
            return False
        except requests.exceptions.HTTPError:
            logging.warning('Communication Error caught, displaying error message')
            self.show_error("Communication Error "+str(response.status_code))
            self.folderitems = {}
            self.status = { 'folders': [] }
            gtk.timeout_add(5000, self.setup_session)
            return True

    def check_activity(self, folders):
        """
        Given the current folder list from the server, determines
        whether there is any network activity and sets a flag in
        self.active
        """
        isactive = False
        active_folder_names = set()
        for folder in folders:
            for peer in folder['peers']:
                if peer['status'].find('<div') != -1:
                    logging.info('Sync activity detected')
                    isactive = True
                    active_folder_names.add(folder['name'])
                    break

        self.active = isactive
        self.active_folder_names = active_folder_names

        if self.active:
            if self.animate == None:
                logging.info('Starting animation loop')
                gtk.timeout_add(1000, self.animate_icon)

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

    def build_folder_menu(self, folder):
	"""
	Build a submenu for the specified folder,
	including items to show the size, open the folder in
	the file manager, show each connected peer, and to 
	copy the secrets to the clipboard.

	Stores references to the size and peer items so they
	can easily be updated.
	"""
	menu = gtk.Menu()

	folderitem = self.folderitems[folder['name']]
	folderitem['sizeitem'] = gtk.MenuItem(folder['status'])
	folderitem['sizeitem'].set_sensitive(False)
	folderitem['sizeitem'].show()
	openfolder = gtk.MenuItem('Open in File Browser')
	openfolder.connect("activate", self.open_fm, folder['name'])
	openfolder.show()

	menu.append(folderitem['sizeitem'])
	menu.append(openfolder)

	if len(folder['peers']) > 0:
	    sep = gtk.SeparatorMenuItem()
	    sep.show()
	    menu.append(sep)
            folderitem['topsepitem'] = sep
	    for peer in folder['peers']:
		buf = self.format_status(peer)
		img = gtk.Image()
		if peer['direct']:
			img.set_from_file(args.iconpath+'/btsync-direct.png')
		else:
			img.set_from_file(args.iconpath+'/btsync-relay.png')
		peeritem = gtk.ImageMenuItem(gtk.STOCK_NEW, buf)
		peeritem.set_image(img)
                peeritem.set_always_show_image(True)
		peeritem.set_sensitive(False)
		peeritem.show()
		folderitem['peeritems'][peer['name']] = peeritem
		menu.append(peeritem)
        else:
            folderitem['topsepitem'] = None

        sep = gtk.SeparatorMenuItem()
	sep.show()
	menu.append(sep)
        folderitem['bottomsepitem'] = sep

        readonlysecret = folder['secret']
        if folder['iswritable']:
                readonlysecret = folder['readonlysecret']
                readwrite = gtk.MenuItem('Get Full Access Secret')
                readwrite.connect("activate", self.copy_secret, folder['secret'])

                readwrite.show()
                menu.append(readwrite)

        readonly = gtk.MenuItem('Get Read Only Secret')
        readonly.connect("activate", self.copy_secret, readonlysecret)

        readonly.show()
        menu.append(readonly)

	return menu
    
    def update_folder_menu(self, folder):
        """
        Updates the submenu for the given folder with the current size
        and updates each peer.
        """
        
        folderitem = self.folderitems[folder['name']]
        folderitem['sizeitem'].set_label(folder['status'])

        menuitem = folderitem['menuitem']

        # we build up this set during check_activity
        # it contains the names of any folders with active peers
        # we display these in the menu with a different icon so that users
        # can see at a glance which of the peers is responsible for a busy icon
        if folder['name'] in self.active_folder_names:
            menuitem.set_label('⇅\t' + folder['name'])
        else:
            menuitem.set_label('―\t' + folder['name'])
        
        menu = menuitem.get_submenu()

        curfolder = [ f for f in self.status['folders'] if folder['name'] == f['name'] ].pop()
        curpeernames = [ peer['name'] for peer in curfolder['peers'] ]
        newpeernames = [ peer['name'] for peer in folder['peers'] ]

        updatepeers = [ peer for peer in folder['peers'] if peer['name'] in curpeernames ]
        newpeers = [ peer for peer in folder['peers'] if peer['name'] not in curpeernames ]
        oldpeers = [ peer for peer in curfolder['peers'] if peer['name'] not in newpeernames ]


        for peer in newpeers:
            bottomseppos = menu.get_children().index(folderitem['bottomsepitem'])
            buf = self.format_status(peer)
            peeritem = gtk.MenuItem(buf)
            peeritem.set_sensitive(False)
            peeritem.show()
            folderitem['peeritems'][peer['name']] = peeritem

            pos = bottomseppos

            if (folderitem['topsepitem'] == None):
                sep = gtk.SeparatorMenuItem()
                sep.show()
                menu.insert(sep, pos)
                folderitem['topsepitem'] = sep
                pos = pos+1

            menu.insert(peeritem, pos)

        for peer in updatepeers:
            buf = self.format_status(peer)
            folderitem['peeritems'][peer['name']].set_label(buf)

        for peer in oldpeers:
            menu.remove(folderitem['peeritems'][peer['name']])
            topseppos = menu.get_children().index(folderitem['topsepitem'])
            bottomseppos = menu.get_children().index(folderitem['bottomsepitem'])
            if (topseppos == bottomseppos-1):
                menu.remove(folderitem['topsepitem'])
                folderitem['topsepitem'] = None


    def show_error(self, message):
        """
        Removes all items from the menu (except quit) and displays an error
        message in their place. Also changes the icon to an error icon.
        """
        self.active = False
        if self.error_item == None:                    
            self.set_icon('-error')

            for child in self.menu.get_children():
                if child == self.sep1:
                    pass
                elif child == self.pause_item:
                    pass
                elif child == self.webui_item:
                    self.webui_item.set_sensitive(False)
                elif child == self.sep2:
                    pass
                elif child == self.debug_item:
                    pass
                elif child == self.quit_item:
                    pass
                else:
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
        self.webui_item.set_sensitive(True)
        if self.error_item != None:
            self.menu.remove(self.error_item)
            self.error_item = None
            self.set_icon('')

    def copy_secret(self, menuitem, secret):
        """
        Copies the supplied secret to the clipboard
        """
    	self.clipboard.set_text(secret)
        logging.info('Secret copied to clipboard')
        logging.debug(secret)
    	return True

    def animate_icon(self):
        """
        Cycles the icon through 3 frames to indicate network activity
        """
        if self.active == False:
            logging.info('Terminating animation loop; Resetting icon')
            self.animate = None
            self.set_icon('')
            self.frame = 0
            return False
        else:
            self.animate = True
            logging.debug('Setting animation frame to {}'.format(self.frame % 3))
            self.set_icon('-active-{}'.format(self.frame % 3))
            self.frame += 1
            return True
        
    def set_icon(self, variant):
        """
        Changes the icon to the given variant
        """
        logging.debug('Setting icon to '+args.iconpath+'/btsync'+variant)
        self.ind.set_icon('btsync'+variant)
        return False

    def open_webui(self, widget):
        """
        Opens a browser to the address of the WebUI indicated in the config file
        """
        logging.info('Opening Web Browser to http://'+self.config['webui']['listen'])
	webbrowser.open(self.webui, 2)
	return True

    def open_fm(self, widget, path):
        logging.info('Opening File manager to '+path)
	if os.path.isdir(path):
	    subprocess.call(['xdg-open', path])

    def toggle_debugging(self, widget):
        """
        Creates or clears the debugging flags for btsync
        """
	filepath = self.config['storage_path']+'/debug.txt'
	if (os.path.isfile(filepath)):
	    os.unlink(filepath)
            logging.info('Bittorrent Sync debugging disabled')
	else:
	    f = open(filepath, 'w')
	    f.write('FFFF')
            logging.info('Bittorrent Sync debugging enabled')
	return True

    def toggle_pause(self, widget):
        """
        handles the pause/resume feature
        """
        btsyncmanager = "/usr/bin/btsync"
        if (os.path.exists(btsyncmanager)):
            try:
                filepath = self.config['storage_path']+'/paused'
                if (os.path.isfile(filepath)):
                    logging.info('Calling '+btsyncmanager+ ' resume')
                    subprocess.check_call([btsyncmanager, 'resume'])
	            logging.info('Bittorrent Sync resumed')
                else:
                    logging.info('Calling '+btsyncmanager+ ' pause')
                    subprocess.check_call([btsyncmanager, 'pause'])
	            logging.info('Bittorrent Sync paused')
            except subprocess.CalledProcessError, e:
                logging.warning('btsync manager failed with status '+e.returncode)
                logging.warning(e.output)
        else:
            logging.error("Could not find BitTorrent Sync Manager at "+btsyncmanager)
        return True

    def get_response_text(self, response):
        """
        Version-safe way to get the response text from a requests module response object
        Older versions use response.content instead of response.text
        """
        return response.text if hasattr(response, "text") else response.content

    def get_response_json(self, response):
	"""
	Version-safe way to parse json from request module response object
	The version in the Ubuntu 12.04 LTS repositories doesnt have .json() 
	"""
	try:
	    response_json = response.json()
	except AttributeError:
	    response_json = json.loads(self.get_response_text(response))
	except TypeError:
	    response_json = json.loads(self.get_response_text(response))
	return response_json

    def main(self):
        gtk.timeout_add(TIMEOUT * 1000, self.setup_session)
        gtk.main()

    def quit(self, widget):
        logging.info('Exiting')
        
        if self.btsync_user:
            logging.info('Running btsync-stopper before exit')
            try:
                stopper = os.path.dirname(os.path.realpath(__file__))+"/btsync-stopper"
                if (os.path.exists(stopper)):
                    logging.info('Calling '+stopper)
                    subprocess.check_call(stopper)
                else:
                    logging.error("Cant find btsync-stopper at "+stopper)
            except subprocess.CalledProcessError, e:
                logging.warning('btsync-stopper failed with status '+e.returncode)
                logging.warning(e.output)
                print "Cannot exit BitTorrent Sync: "+e.output
                print "Please exit BitTorrent Sync manually"

        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', 
                        default=os.environ['HOME']+'/.btsync.conf',
                        help="Location of BitTorrent Sync config file")
    parser.add_argument('--iconpath', 
                        default=os.path.dirname(os.path.realpath(__file__))+"/icons",
                        help="Path to icon theme folder")
    parser.add_argument('-v', '--version',
			action='store_true',
                        help="Print version information and exit")
    parser.add_argument('--log',
                        default='WARNING',
                        help="Set logging level")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)

    logging.basicConfig(level=numeric_level)

    if (args.version):
	print os.path.basename(__file__)+" Version "+VERSION
	exit()

    btconf = BtSyncConfig()

    with file_lock(btconf.config['storage_path'] + '/indicator.lock'):
        indicator = BtSyncIndicator(btconf)
        indicator.main()

