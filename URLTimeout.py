#!/usr/bin/python
# URLTimeout module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# URLTimeout class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites.	
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

from URLTimeoutCommon import *

debug = False

class URLTimeout:
	def __init__(self,debug=False):
		self.debug = debug
		try:
			from URLTimeoutCurl import URLTimeoutCurl
			self.ut = URLTimeoutCurl()
		except ImportError,e:
			if debug:
				print "PyCurl importing error",e
			try:
				from URLTimeoutAsync import URLTimeoutAsync
				self.ut = URLTimeoutAsync()
			except ImportError,e:
				print "Async importing error",e
				raise Exception, "Install Python >=2.3 (for asyncchat) or PyCurl, 'cause neither work right now!"
				return
		
		self.get_url = self.ut.get_url

		if "auth" in dir(self.ut):
			self.auth = self.ut.auth

URLTimeout.URLTimeoutError = URLTimeoutError

URLTimeout.URLOldDataError = URLOldDataError
