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
				mod = __import__(m, globals(), locals(), [m], -1)
				self.__ut = getattr(mod,m)(debug=debug)
				break
			except ImportError,e:
				if debug:
					print "%s importing error"%m,e
		else:
			raise Exception, "Install Python >=2.3 (for asyncchat) or PyCurl, 'cause neither work right now!"
		
		for method in dir(self.__ut):
			if method[0]!="_":
				setattr(self,method,getattr(self.__ut,method))

if __name__ == "__main__":
	obj = URLTimeout(debug=True).get_url("http://www.google.com")
	print obj
