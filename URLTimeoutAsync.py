#!/usr/bin/python
# URLTimeout module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# URLTimeoutAsync class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites, using the Python 2.3 asynccore/http modules
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import urlparse,urllib2,socket
import asyncore
import asynchttp
from urllib import urlencode

from alarms import AsyncAlarmMixin
from URLTimeoutCommon import *
from local_dict import apply_vars

debug = True

class asyncgrab(AsyncAlarmMixin,asynchttp.AsyncHTTPConnection):
	def __init__(self, uts, url,referer=None,headers={},debug=False, data = None):
		self.data = data
		origurl = url

		resp = handleurl(url)
		if resp!=None:
			self.response = resp
			self.handle_response()

		bits = urlparse.urlsplit(url)
		self.debug = debug
		if self.debug:
			print "bits",bits
		if bits[1].find(':')==-1:
			asynchttp.AsyncHTTPConnection.__init__(self, bits[1], 80)
		else:
			asynchttp.AsyncHTTPConnection.__init__(self, bits[1][:bits[1].find(':')], int(bits[1][bits[1].find(':'):]))
		AsyncAlarmMixin.__init__(self)
		self.set_relative_alarm(uts.getTimeout())
		url = bits[2]
		if len(bits[3])>0:
			url += "?"+bits[3]
		if len(url)==0:
			url="/"
		if self.debug:
			print "url",url
		self._url = url
		self._referer = referer
		self._closed = False
		self._headers = headers
		
	def handle_response(self):
		if not self._closed:
			self.close()
			self._closed = True
			self.die_now = True
		else:
			print "we already killed this (response)"		

	def handle_connect(self):
		#print "connect!"
		asynchttp.AsyncHTTPConnection.handle_connect(self)
		if self.data == None:
			self.putrequest("GET", self._url)
		else:
			self.putrequest("POST", self._url)
		if self._referer!=None:
			self.putheader("Referer",self._referer)
		if self._headers:
			for k in self._headers.keys():
				self.putheader(k,self._headers[k])
		if self.data:
			self.putheader('Content-Length', str(len(self.data)))
			
		self.endheaders()
		if self.data != None:
			self.send_entity(self.data)
		self.getresponse()
	
	def connect(self):
		asynchttp.AsyncHTTPConnection.connect(self)
	
	def handle_alarm(self, data):
		if not self._closed:
			self.close()
			self._closed = True
			self.die_now = True
		else:
			print "we already killed this (alarm)"		

class URLTimeoutAsync(URLGetter):
	def get_url(self,url,**kwargs):
		kwargs = apply_vars(kwargs, self.get_url_args)
		exec('pass') # apply locals. Copy+paste magic...
		data = kwargs['data'] # doesn't seem to work via other mechanism for some bizarre reason

		if proxy!=None:
			raise Exception, "URLTimeoutAsync can't handle proxies right now!"

		if data!=None:
			encode_data = urlencode(data)
		else:
			encode_data = None
		grab = asyncgrab(self,url,ref,headers,data=encode_data,debug=self.debug)
		if self.debug:
			grab.set_debuglevel(1)
		try:
			grab.connect()
		except socket.error,err:
			raise URLTimeoutError,(err[1],url)

		grab.loop(timeout=self.getTimeout())

		if not hasattr(grab, "response") or grab.response.body==None:
			print grab.__dict__
			raise URLTimeoutError, ("Timed out!",url)
		
		info = self.gen_headers(grab.response.msg.headers)
		ret = self.check_move(grab.response.status, locals())
		if ret!=None:
			return ret
		
		if grab.response.status == 304: # old data!
			raise URLOldDataError
		
		if grab.response.status !=200:
			raise URLTimeoutError,(str(grab.response.status)+" "+grab.response.reason,url,grab.response.status)
		
		return URLObject(url,ref,grab.response.body,info)
