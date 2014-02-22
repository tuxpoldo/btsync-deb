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

import json
import logging
import requests

class BtSyncApi(object):
	"""
	The BtSyncApi class is a light wrapper around the Bittorrent Sync API.
	Currently to use the API you will need to apply for a key. You can find out
	how to do that, and learn more about the btsync API here:

	http://www.bittorrent.com/sync/developers/api

	The docstrings of this class' methods were copied from the above site.
	"""

	def __init__(self, host='localhost', port='8888', username=None, password=None):
		"""
		Parameters
		----------
		host : str
		    IP address that the btsync api responds at.
		port : str
		    Port that the btsync api responds at.
		username : str
		    optional username to use if btsync api is protected.
		password : str
		    optional password to use if btsync api is protected.

		Notes
		-----
		The host, port, username, and password must match the config.json file.

		"""
		if username is None or password is None:
			self.auth = None
		else:
			self.auth = (username,password)
		self.urlroot = 'http://'+host+':'+str(port)+'/api'
		self.response = None

	def get_folders(self,secret=None,throw_exceptions=True):
		"""
		Returns an array with folders info. If a secret is specified, will
		return info about the folder with this secret.

		[
			{
				"dir": "\\\\?\\D:\\share",
				"secret": "A54HDDMPN4T4BTBT7SPBWXDB7JVYZ2K6D",
				"size": 23762511569,
				"type": "read_write",
				"files": 3206,
				"error": 0,
				"indexing": 0
			}
		]

		http://[address]:[port]/api?method=get_folders[&secret=(secret)]

		secret (optional) - if a secret is specified, will return info about
		the folder with this secret
		"""
		params = {'method': 'get_folders'}
		if secret is not None:
			params['secret'] = secret
		return self._request(params,throw_exceptions)

	def add_folder(self,folder,secret=None,selective_sync=False,throw_exceptions=True):
		"""
		Adds a folder to Sync. If a secret is not specified, it will be
		generated automatically. The folder will have to pre-exist on the disk
		and Sync will add it into a list of syncing folders.
		Returns '0' if no errors, error code and error message otherwise.

		{ "error": 0 }

		http://[address]:[port]/api?method=add_folder&dir=(folderPath)[&secret=(secret)&selective_sync=1]

		dir (required)				- specify path to the sync folder
		secret (optional)			- specify folder secret
		selective_sync (optional)	- specify sync mode, selective - 1,
										all files (default) - 0
		"""
		params = {'method': 'add_folder', 'dir': folder }
		if secret is not None:
			params['secret'] = secret
		if selective_sync:
			params['selective_sync'] = 1

	def remove_folder(self,secret,throw_exceptions=True):
		"""
		Removes folder from Sync while leaving actual folder and files on
		disk. It will remove a folder from the Sync list of folders and
		does not touch any files or folders on disk. Returns '0' if no error,
		'1' if there’s no folder with specified secret.

		{ "error": 0 }

		http://[address]:[port]/api?method=remove_folder&secret=(secret)

		secret (required) - specify folder secret
		"""
		params = { 'method': 'remove_folder', 'secret' : secret }
		return self._request(params,throw_exceptions)

	def get_files(self,secret,path=None,throw_exceptions=True):
		"""
		Returns list of files within the specified directory. If a directory is
		not specified, will return list of files and folders within the root
		folder. Note that the Selective Sync function is only available in the
		API at this time.

		[
			{
				"name": "images",
				"state": "created",
				"type": "folder"
			},
			{
				"have_pieces": 1,
				"name": "index.html",
				"size": 2726,
				"state": "created",
				"total_pieces": 1,
				"type": "file",
				"download": 1 // only for selective sync folders
			}
		]

		http://[address]:[port]/api?method=get_files&secret=(secret)[&path=(path)]

		secret (required) - must specify folder secret
		path (optional) - specify path to a subfolder of the sync folder.
		"""
		params = { 'method': 'get_files', 'secret' : secret }
		if path is not None:
			params['path'] = path
		return self._request(params,throw_exceptions)

	def set_file_preferences(self,secret,path,download,throw_exceptions=True):
		"""
		Selects file for download for selective sync folders. Returns file
		information with applied preferences.

		http://[address]:[port]/api?method=set_file_prefs&secret=(secret)&path=(path)&download=1

		secret (required)	- must specify folder secret
		path (required)		- specify path to a subfolder of the sync folder.
		download (required)	- specify if file should be downloaded (yes - 1, no - 0)		
		"""
		params = {
			'method': 'set_file_preferences',
			'secret': secret,
			'path': path,
			'download': download
		}
		if path is not None:
			params['path'] = path
		return self._request(params,throw_exceptions)

	def get_folder_peers(self,secret,throw_exceptions=True):
		"""
		Returns list of peers connected to the specified folder.

		[
		    {
			"id": "ARRdk5XANMb7RmQqEDfEZE-k5aI=",
			"connection": "direct", // direct or relay
			"name": "GT-I9500",
			"synced": 0, // timestamp when last sync completed
			"download": 0,
			"upload": 22455367417
		    }
		]

		http://[address]:[port]/api?method=get_folder_peers&secret=(secret)

		secret (required) - must specify folder secret
		"""
		params = { 'method': 'get_folder_peers', 'secret' : secret }
		return self._request(params,throw_exceptions)

	def get_secrets(self,secret=None,encryption=False,throw_exceptions=True):
		"""
		Generates read-write, read-only and encryption read-only secrets.
		If ‘secret’ parameter is specified, will return secrets available for
		sharing under this secret.
		The Encryption Secret is new functionality. This is a secret for a
		read-only peer with encrypted content (the peer can sync files but can
		not see their content). One example use is if a user wanted to backup
		files to an untrusted, unsecure, or public location. This is set to
		disabled by default for all users but included in the API.

		{
			"read_only": "ECK2S6MDDD7EOKKJZOQNOWDTJBEEUKGME",
			"read_write": "DPFABC4IZX33WBDRXRPPCVYA353WSC3Q6",
			"encryption": "G3PNU7KTYM63VNQZFPP3Q3GAMTPRWDEZ”
		}

		http://[address]:[port]/api?method=get_secrets[&secret=(secret)&type=encryption]

		secret (required) - must specify folder secret
		type (optional) - if type=encrypted, generate secret with support of encrypted peer
		"""
		params = { 'method': 'get_secrets' }
		if secret is not None:
			params['secret'] = secret
		if encryption:
			params['type'] = 'encryption'
		return self._request(params,throw_exceptions)

	def get_folder_prefs(self,secret,throw_exceptions=True):
		"""
		Returns preferences for the specified sync folder.

		{
			"search_lan":1,
			"use_dht":0,
			"use_hosts":0,
			"use_relay_server":1,
			"use_sync_trash":1,
			"use_tracker":1
		}

		http://[address]:[port]/api?method=get_folder_prefs&secret(secret)

		secret (required) - must specify folder secret
		"""
		params = { 'method': 'get_folder_prefs', 'secret' : secret }
		return self._request(params,throw_exceptions)

	def set_folder_prefs(self,secret,prefs_dictionary,throw_exceptions=True):
		"""
		Sets preferences for the specified sync folder. Parameters are the same
		as in ‘Get folder preferences’. Returns current settings.

		http://[address]:[port]/api?method=set_folder_prefs&secret=(secret)&param1=value1&param2=value2,...

		secret (required) - must specify folder secret
		params - { use_dht, use_hosts, search_lan, use_relay_server, use_tracker, use_sync_trash }
		"""
		params = { 'method': 'set_folder_prefs', 'secret' : secret }
		params.update (prefs_dictionary)
		return self._request(params,throw_exceptions)

	def get_folder_hosts(self,secret,throw_exceptions=True):
		"""
		Returns list of predefined hosts for the folder, or error code if a
		secret is not specified.

		{
			"hosts" : ["192.168.1.1:4567",
			"example.com:8975"]
		}

		http://[address]:[port]/api?method=get_folder_hosts&secret=(secret)

		secret (required) - must specify folder secret
		"""
		params = { 'method': 'get_folder_hosts', 'secret' : secret }
		return self._request(params,throw_exceptions)

	def set_folder_hosts(self,secret,hosts_list = [],throw_exceptions=True):
		"""
		Sets one or several predefined hosts for the specified sync folder.
		Existing list of hosts will be replaced. Hosts should be added as values
		of the ‘host’ parameter and separated by commas.
		Returns current hosts if set successfully, error code otherwise.

		http://[address]:[port]/api?method=set_folder_hosts&secret=(secret)&hosts=host1:port1,host2:port2,...

		secret (required)	- must specify folder secret
		hosts (required)	- enter list of hosts separated by comma.
								Host should be represented as “[address]:[port]”
		"""
		params = {
			'method': 'set_folder_hosts',
			'secret': secret,
			'hosts': hosts_list
		}
		return self._request(params,throw_exceptions)

	def get_prefs(self,throw_exceptions=True):
		"""
		Returns BitTorrent Sync preferences. Contains dictionary with
		advanced preferences. Please see Sync user guide for description
		of each option.

		{
			"device_name" : "iMac",
			"disk_low_priority": "true",
			"download_limit": 0,
			"folder_rescan_interval": "600",
			"lan_encrypt_data": "true",
			"lan_use_tcp": "false",
			"lang": -1,
			"listening_port": 11589,
			"max_file_size_diff_for_patching": "1000",
			"max_file_size_for_versioning": "1000",
			"rate_limit_local_peers": "false",
			"send_buf_size": "5",
			"sync_max_time_diff": "600",
			"sync_trash_ttl": "30",
			"upload_limit": 0,
			"use_upnp": 0,
			"recv_buf_size": "5"
		}
		"""
		params = {'method': 'get_prefs'}
		return self._request(params,throw_exceptions)

	def set_prefs(self,prefs_dictionary,throw_exceptions=True):
		"""
		Sets BitTorrent Sync preferences. Parameters are the same as in
		'Get preferences'. Advanced preferences are set as general
		 settings. Returns current settings.
		"""
		params = {'method': 'set_prefs'}
		params.update (prefs_dictionary)
		return self._request(params,throw_exceptions)

	def get_os(self,throw_exceptions=True):
		"""
		Returns OS name where BitTorrent Sync is running.

		{ "os": "win32" }

		http://[address]:[port]/api?method=get_os
		"""
		params = {'method': 'get_os'}
		return self._request(params,throw_exceptions)

	def get_version(self,throw_exceptions=True):
		"""
		Returns BitTorrent Sync version.

		{ "version": "1.2.48" }

		http://[address]:[port]/api?method=get_version
		"""
		params = {'method': 'get_version'}
		return self._request(params,throw_exceptions)

	def get_speed(self,throw_exceptions=True):
		"""
		Returns current upload and download speed.

		{
		    "download": 61007,
		    "upload": 0
		}

		http://[address]:[port]/api?method=get_speed
		"""
		params = {'method': 'get_speed'}
		return self._request(params,throw_exceptions)


	def shutdown(self,throw_exceptions=True):
		"""
		Gracefully stops Sync.

		{ "error" : 0 }

		http://[address]:[port]/api?method=shutdown
		"""
		params = {'method': 'shutdown'}
		return self._request(params,throw_exceptions)




	def get_status_code(self):
		"""
		Returns the HTTP status code of the last operation
		"""
		return self.response.status_code
		

	def _request(self,params,throw_exceptions):
		"""
		Internal function that handles the communication with btsync
		"""
		if throw_exceptions:
			self.response = requests.get(self.urlroot, params=params, auth=self.auth)
			self.response.raise_for_status()
			return json.loads (self._get_response_text())

		try:
			self.response = requests.get(self.urlroot, params=params, auth=self.auth)
			self.response.raise_for_status()
			return json.loads (self._get_response_text())
		except requests.exceptions.ConnectionError:
			logging.warning("Couldn't connect to Bittorrent Sync")
			return None
		except requests.exceptions.HTTPError:
			logging.warning('Communication Error ' + str(response.status_code))
			return None

	def _get_response_text(self):
		"""
		Version-safe way to get the response text from a requests module response object
		Older versions use response.content instead of response.text
		"""
		return self.response.text if hasattr(self.response, "text") else self.response.content



