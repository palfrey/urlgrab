#!/usr/bin/python
# Comics Grabber by Tom Parker <palfrey@bits.bris.ac.uk>
# http://www.bits.bris.ac.uk/palfrey/
#
# URLTimeoutCurl class
# Grabs URLs, but with a timeout to avoid locking on crapped-up sites.	
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

import pycurl,re
from URLTimeoutCommon import *
from urllib import urlencode

class URLTimeoutCurl(URLGetter):
	def __init__(self, debug = False):
		URLGetter.__init__(self, debug)
		self.user = ""
		self.write_callback = None

	def body_callback(self, buf):
		self.contents += buf
		if self.write_callback!=None:
			self.write_callback(len(self.contents))
	
	def head_callback(self, buf):
		self.header = self.header + buf

	def auth(self,user,password):
		self.user = user
		self.password = password

	def get_url(self,url,ref=None,headers={},data=None,ignore_move=False):
		resp = handleurl(url)
		if resp!=None:
			return URLObject(url,None,resp.body,resp.msg.headers)
	
		self.contents = ""
		self.header = ""
		origurl = url
		c = pycurl.Curl()
		if self.user!="":
			c.setopt(c.HTTPAUTH,c.HTTPAUTH_BASIC)
			c.setopt(c.USERPWD,"%s:%s"%(self.user,self.password))
		c.setopt(c.URL, str(url))
		c.setopt(c.WRITEFUNCTION, self.body_callback)
		c.setopt(c.HEADERFUNCTION, self.head_callback)
		c.setopt(c.HTTPHEADER,[x+": "+headers[x] for x in headers.keys()])

		if data!=None:
			enc = urlencode(data)
			#c.setopt(c.POST,1)
			c.setopt(c.POSTFIELDS,enc)
			print "enc",enc
			
		c.setopt(c.LOW_SPEED_LIMIT, 15) # 15 bytes/sec = dead. Random value.
		c.setopt(c.LOW_SPEED_TIME, self.getTimeout()) # i.e. dead (< 15 bytes/sec) 
		if ref!=None:
			c.setopt(c.REFERER, ref)

		try:
			c.perform()
		except pycurl.error, msg:
			raise URLTimeoutError,(msg[1],url)
			
		c.close()
		
		if self.contents=="" and self.header == "":
			raise URLTimeoutError, ("Timed out!",url)
		
		info = {}
		status = 0
		hdrs = self.header.splitlines()

		if hdrs != []:
			last_ok = 0
			for x in range(len(hdrs)):
				if hdrs[x].find("HTTP")==0:
					last_ok = x
			hdrs = hdrs[last_ok:]
			ret = re.search("HTTP/1.[01] (\d+) (.*?)",hdrs[0]).group(1,2)
			status = [0,0]
			status[0] = int(ret[0])
			status[1] = ret[1]

			info = self.gen_headers(hdrs[1:])
			
			ret = self.check_move(status[0], locals())
			if ret!=None:
				return ret
			
			if status[0] == 304:
				raise URLOldDataError
			
			if status[0] !=200:
				raise URLTimeoutError,(str(status[0])+" "+status[1],url)
		
			return URLObject(origurl,None,self.contents,info)
		raise URLTimeoutError,("No Headers!",url)
