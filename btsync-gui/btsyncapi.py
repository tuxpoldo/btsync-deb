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
		"""
		params = { 'method': 'get_folder_peers', 'secret' : secret }
		return self._request(params,throw_exceptions)

	def remove_folder(self,secret,throw_exceptions=True):
		"""
		Removes folder from Sync while leaving actual folder and files on
		disk. It will remove a folder from the Sync list of folders and
		does not touch any files or folders on disk. Returns '0' if no error,
		'1' if there’s no folder with specified secret.

		{ "error": 0 }
		"""
		params = { 'method': 'remove_folder', 'secret' : secret }
		return self._request(params,throw_exceptions)

	def get_version(self,throw_exceptions=True):
		"""
		Returns BitTorrent Sync version.

		{ "version": "1.2.48" }
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
		"""
		params = {'method': 'get_speed'}
		return self._request(params,throw_exceptions)

	def get_os(self,throw_exceptions=True):
		"""
		Returns OS name where BitTorrent Sync is running.

		{ "os": "win32" }
		"""
		params = {'method': 'get_os'}
		return self._request(params,throw_exceptions)

	def shutdown(self,throw_exceptions=True):
		"""
		Gracefully stops Sync.

		{ "error" : 0 }
		"""
		params = {'method': 'shutdown'}
		return self._request(params,throw_exceptions)

	def get_status_code(self):
		return self.response.status_code
		

	def _request(self,params,throw_exceptions):
		"""
		Internal function that handles the communication with btsync
		"""
		if throw_exceptions:
			self.response = requests.get(self.urlroot, params=params, auth=self.auth)
			self.response.raise_for_status()
			return json.loads (self._get_response_text(self.response))

		try:
			response = requests.get(self.urlroot, params=params, auth=self.auth)
			response.raise_for_status()
			return json.loads (self._get_response_text(response))
		except requests.exceptions.ConnectionError:
			logging.warning("Couldn't connect to Bittorrent Sync")
			return None
		except requests.exceptions.HTTPError:
			logging.warning('Communication Error ' + str(response.status_code))
			return None

	def _get_response_text(self, response):
		"""
		Version-safe way to get the response text from a requests module response object
		Older versions use response.content instead of response.text
		"""
		return response.text if hasattr(response, "text") else response.content



