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
		modules = ("URLTimeoutCurl", "URLTimeoutAsync")
		for m in modules:
			try:
				mod = __import__(m, globals(), locals(), [m], -1)
				self.__ut = mod(debug=debug)
			except ImportError,e:
				if debug:
					print "%s importing error"%m,e
		else:
			raise Exception, "Install Python >=2.3 (for asyncchat) or PyCurl, 'cause neither work right now!"
		
		for method in dir(self.__ut):
			if method[0]!="_":
				setattr(self,method,getattr(self.__ut,method))

URLTimeout.URLTimeoutError = URLTimeoutError

URLTimeout.URLOldDataError = URLOldDataError

if __name__ == "__main__":
	obj = URLTimeout(debug=True).get_url("http://www.google.com")
	print obj
