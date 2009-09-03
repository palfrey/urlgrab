#!/usr/bin/python
# URLTimeout module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# URLTimeoutCommon class
# common stuff for the other URLTimeout* modules
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)
debug = False

from sys import version_info
from urlparse import urljoin
from local_dict import apply_vars
from os import SEEK_SET, SEEK_CUR, SEEK_END

class URLTimeoutError(Exception):
	def __init__(self,string,url):
		Exception.__init__(self,string)
		self.url = url

class URLOldDataError(Exception):
	pass

			
class URLHeaders:
	def __init__(self,headers):
		self.headers = headers
		if debug:
			print self.headers
		self.dict = self.headers
	
	def getmime(self):
		ct = ""
		if self.headers.has_key("Content-Type"):
			ct = self.headers["Content-Type"]
		elif self.headers.has_key("Content-type"):
			ct = self.headers["Content-type"]
		else:
			raise Exception, "No content type header!"
		mime = ct.split("/",1)
		mime[1:] = mime[1].split(";",1)
		if version_info >= (2,3,0):
			mime[1] = mime[1].strip("\r\n")
		else:
			mime[1] = mime[1].strip()
		if mime[1][-1]=='\r' or mime[1][-1]=='\n':
			raise Exception
		
		mime = mime[:2]
		return mime
	
	def get(self,name,alternate=None):
		if self.headers.has_key(name):
			return name
		else:
			return alternate
	
	def cookies(self):
		if not self.headers.has_key("Set-Cookie"):
			raise Exception, "No Set-Cookie header"
		return dict([x.split(";")[0].split("=") for x in self.headers["Set-Cookie"]])
	
	def getheader(self,name):
		return self.get(name,None)
	
	def getmaintype(self):
		return self.getmime()[0]
		
	def getsubtype(self):
		return self.getmime()[1]

import codecs
if codecs.__dict__.has_key("BOM_UTF16_LE"):
	codec = {codecs.BOM_UTF16_LE:codecs.lookup('utf_16_le'),codecs.BOM_UTF16_BE:codecs.lookup('utf_16_be')}
else:
	codec = {}
ascii = codecs.lookup('ascii')[0]

class URLObject:
	def __init__(self,url,ref,data,headers={}):
		self.url = url
		self.data = data
		self.ref = ref
		self.headers = URLHeaders(headers)
		self.location = 0
		
		if data!=None and headers!={} and self.getmime()[0] !="image":
			for x in codec.keys():
				if self.data[0:len(x)] == x:
					self.data = ascii(codec[x][1](self.data[len(x):])[0])[0]
					print "recoded",url
					break			
	
	def geturl(self):
		return self.url
	
	def info(self):
		return self.headers
	
	def readall(self):
		return self.data
	
	def read(self, length=-1):
		if length < 0:
			ret = self.data[self.location:len(self.data)]
			self.location = len(self.data)
			return ret
		elif self.location<len(self.data):
			ret = self.data[self.location:self.location+length]
			self.location += length
			if self.location > len(self.data):
				self.location = len(self.data)
			return ret
		else:
			return ""
	
	def tell(self):
		return self.location

	def seek(self, offset, whence = SEEK_SET):
		if whence == SEEK_SET:
			self.location = offset
		elif whence == SEEK_CUR:
			self.location += offset
		elif whence == SEEK_END:
			self.location = len(self.data)-offset

		if self.location > len(self.data):
			self.location = len(self.data)
		elif self.location < 0:
			self.location = 0

	def close(self):
		pass
	
	def getmime(self):
		return self.headers.getmime()

class URLGetter:
	def __init__(self,debug = False):
		self.timeout = 40
		self.debug = debug
		
	def setTimeout(self, val):
		self.timeout = val
	
	def getTimeout(self):
		return self.timeout

	def get_url(self,*args):
		raise Exception, "Warning: subclass has not defined get_url"

	get_url_args = ('headers','proxy','ref','ignore_move')

	def check_move(self, status, kwargs):
		apply_vars(kwargs)
		exec('pass') # apply locals. Copy+paste magic...
		if not ignore_move and (status in (301,302,303)): # moved
			try:
				if info.has_key("location"):
					newuri = info["location"]
				elif info.has_key("Location"):
					newuri = info["Location"]
				else:
					print "info",info
					raise URLTimeoutError,("301/302/303, but no location!",url)
				del kwargs['url']
				del kwargs['self']
				return self.get_url(urljoin(url,newuri),**kwargs)
					
			except:
				print "info",info
				raise
		return None
		
from Enum import enum
from os import popen
from os.path import dirname,basename
import urlparse

kind = enum('http','file','python')

def getkind(url):
	bits = urlparse.urlsplit(url)
	newurl ="".join(bits[1:])
	while newurl[0]=="/":
		newurl = newurl[1:]
	try:
		return (kind(bits[0]),newurl)
	except KeyError:
		print "bits",bits
		raise

class URLPython:
	def __init__(self,url,debug=False):
		if debug:
			print "made urlpython"
		self._url = url
		cmd = "cd %s;python %s"%(dirname(url),basename(url))
		print "cmd",cmd
		data = popen(cmd,"r").readlines()
		self.msg = URLHeaders({})
		self.status = 200
		self.body = "".join(data[2:])

class URLFile:
	def __init__(self,url,debug=False):
		if debug:
			print "made asyncfile"
		self._url = url
		try:
			self.body = file(self._url).read()
		except IOError,e:
			raise URLTimeoutError, (str(e),url)
		self.msg = URLHeaders({})
		self.status = 200

def handleurl(url):
	(mykind,rest) = getkind(url)
	#print "kind",url,mykind,rest
	if mykind == kind.file:
		return URLFile(rest)
	elif mykind == kind.python:
		return URLPython(rest)
	elif mykind == kind.http:
		return None
	
