#!/usr/bin/python
# URLTimeout module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# URLTimeout class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites.	
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

class URLTimeout:
	def __init__(self,debug=False):
		self.debug = debug
		modules = ("URLTimeoutCurl", "URLTimeoutAsync", "URLTimeoutAppEngine")
		for m in modules:
			try:
				mod = __import__(m, globals(), locals(), [m])
				self.__ut = getattr(mod,m)(debug=debug)
				break
			except ImportError,e:
				if debug:
					print "%s importing error:"%m,e
		else:
			raise Exception, "Install Python >=2.3 (for asyncchat) or PyCurl, 'cause neither work right now!"
		
	def get(self,url,ref=None,headers={},data=None,ignore_move=False, proxy=None):
		return self.__ut.get(url,ref=ref,headers=headers,data=data,ignore_move=ignore_move, proxy=proxy)

	def auth(self,user,password):
		return self.__ut.auth(user,password)

	def setTimeout(self, val):
		self.__ut.setTimeout(val)
	
	def getTimeout(self):
		return self.__ut.getTimeout(val)

if __name__ == "__main__":
	obj = URLTimeout(debug=True).get("http://www.google.com")
	print obj
