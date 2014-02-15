
import requests
import json

class BtSyncApi(object):
	"""
	The BtSyncApi class is a light wrapper around the Bittorrent Sync API.
	Currently to use the API you will need to apply for a key. You can find out
	how to do that, and learn more about the btsync API here:

	http://www.bittorrent.com/sync/developers/api

	The docstrings of this class' methods were copied from the above site.
	"""

	def __init__(self, host='localhost', port='8888', user=None, password=None):
		"""
		Parameters
		----------
		host : str
		    IP address that the btsync api responds at.
		port : str
		    Port that the btsync api responds at.
		user : str
		    optional username to use if btsync api is protected.
		pswd : str
		    optional password to use if btsync api is protected.

		Notes
		-----
		The host, port, user, and pswd must match the config.json file.

		"""
		if user is not None or password is not None:
			self.auth = None
		else:
			self.auth = (user,password)
		self.urlroot = 'http://'+host+':'+str(port)+'/api'

	def get_prefs(self):
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
		return self._request(params)

	def set_prefs(self,prefsdict):
		"""
		Sets BitTorrent Sync preferences. Parameters are the same as in
		'Get preferences'. Advanced preferences are set as general
		 settings. Returns current settings.
		"""
		params = {'method': 'set_prefs'}
		params.update (prefsdict)
		return self._request(params)

	def get_folders(self, secret=None):
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
		return self._request(params)

	def _request(self,params):
		"""
		Internal function that handles the communication with btsync
		"""
		try:
			response = requests.get(self.urlroot, params=params, auth=self.auth)
			response.raise_for_status()
			return json.loads (self._get_response_text(response))
		except requests.exceptions.ConnectionError:
			print "Couldn't connect to Bittorrent Sync"
			return None
		except requests.exceptions.HTTPError:
			print "Communication Error " + str(response.status_code)
			return None

	def _get_response_text(self, response):
		"""
		Version-safe way to get the response text from a requests module response object
		Older versions use response.content instead of response.text
		"""
		return response.text if hasattr(response, "text") else response.content



