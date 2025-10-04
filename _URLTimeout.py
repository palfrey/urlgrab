#!/usr/bin/python
# URLTimeout module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# URLTimeout class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites.	
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import importlib

from urlgrab._URLTimeoutCommon import URLObject

class URLTimeout:
	def __init__(self,debug=False):
		self.debug = debug
		modules = ("URLTimeoutRequests", "URLTimeoutCurl", "URLTimeoutAppEngine")
		for m in modules:
			try:
				if __name__.find("._URLTimeout") != -1:
					path = __name__.replace("._URLTimeout", "")
				else:
					path = "urlgrab"
				if debug:
					print("path", path)
				mod = importlib.import_module(".%s" % m, package=path)
				self.__ut = getattr(mod,m)(debug=debug)
				if debug:
					print("using %s" % m)
				break
			except ImportError as e:
				if debug:
					print("%s importing error:" % m)
					print(e)
		else:
			raise Exception("Install Python >=2.3 (for asyncchat) or PyCurl, 'cause neither work right now!")
		
	def get(self,url,ref=None,headers={},data=None,ignore_move=False, proxy=None) -> URLObject:
		return self.__ut.get(url,ref=ref,headers=headers,data=data,ignore_move=ignore_move, proxy=proxy)

	def auth(self,user,password):
		return self.__ut.auth(user,password)

	def setTimeout(self, val):
		self.__ut.setTimeout(val)
	
	def getTimeout(self):
		return self.__ut.getTimeout()

	def __repr__(self):
	    return str(self.__ut)

if __name__ == "__main__":
	obj = URLTimeout(debug=True).get("http://www.google.com")
	print(obj)
