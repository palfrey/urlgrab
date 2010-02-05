#!/usr/bin/python
# URLTimeout module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# URLTimeoutAppEngine class
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

from urllib import urlencode

from _URLTimeoutCommon import *
from _local_dict import apply_vars

from google.appengine.api.urlfetch import fetch, DownloadError

class URLTimeoutAppEngine(URLGetter):
	def auth(self,user,password):
		raise Exception, "URLTimeoutAppEngine doesn't do basic auth yet!"

	def get_url(self,url,**kwargs):
		kwargs = apply_vars(kwargs, self.get_url_args)
		exec('pass') # apply locals. Copy+paste magic...
		data = kwargs['data'] # doesn't seem to work via other mechanism for some bizarre reason

		if proxy!=None:
			raise Exception, "URLTimeoutAppEngine can't handle proxies right now!"

		if data!=None:
			data = urlencode(data)
		if ref!=None:
			headers["Referer"] = ref
		try:
			grab = fetch(url,payload=data,headers=headers,deadline=self.getTimeout())
		except DownloadError,e:
			raise URLTimeoutError,(e.message,url)

		ret = self.check_move(grab.status_code, locals())
		if ret!=None:
			return ret
		
		if grab.status_code == 304: # old data!
			raise URLOldDataError
		
		if grab.status_code !=200:
			raise URLTimeoutError,(str(grab.status_code)+" "+grab.content,url, grab.status_code)
		
		return URLObject(url,ref,grab.content,grab.headers)

#if __name__ == '__main__':
	#print urllib2.urlopen("http://eris")

#	print ret.info().getmime()
