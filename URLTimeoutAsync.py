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

debug = True

class asyncgrab(AsyncAlarmMixin,asynchttp.AsyncHTTPConnection):
	def __init__(self, url,referer=None,headers={},debug=False, data = None):

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
		self.set_relative_alarm(12)
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
		for k in self._headers.keys():
			self.putheader(k,self._headers[k])
		if self.data!=None:
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


class URLTimeoutAsync:
	def __init__(self,debug=False):
		self.debug = debug

	def get_url(self,url,ref,headers,data=None):
		origurl = url
		if data!=None:
			data = urlencode(data)
		grab = asyncgrab(url,ref,headers,data=data,debug=self.debug)
		if self.debug:
			grab.set_debuglevel(1)
		try:
			grab.connect()
		except socket.error,err:
			raise URLTimeoutError,(err[1],url)

		grab.loop(timeout=15)

		if not hasattr(grab, "response") or grab.response.body==None:
			print grab.__dict__
			raise URLTimeoutError, ("Timed out!",url)
		
		info = {}
		for hdr in grab.response.msg.headers:
			(type,data) = hdr.split(':',1)
			info[type] = data[1:]
			while (info[type][-1]=='\r' or info[type][-1]=='\n'):
				info[type] = info[type][:-1]

		if grab.response.status == 301: # moved permenantly
			return self.get_url(info["Location"],ref,headers)
		
		if grab.response.status == 304: # old data!
			raise URLOldDataError
		
		if grab.response.status !=200:
			raise URLTimeoutError,(str(grab.response.status)+" "+grab.response.reason,url)
		
		return URLObject(origurl,ref,grab.response.body,info)

#if __name__ == '__main__':
	#print urllib2.urlopen("http://eris")

#	print ret.info().getmime()
