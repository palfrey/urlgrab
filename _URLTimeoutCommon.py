#!/usr/bin/python
# URLTimeout module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# URLTimeoutCommon class
# common stuff for the other URLTimeout* modules
#	
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)

from sys import version_info
from urlparse import urljoin
from _local_dict import apply_vars
try:
	from os import SEEK_SET, SEEK_CUR, SEEK_END
except ImportError: # python <2.5
	SEEK_SET = 0
	SEEK_CUR = 1
	SEEK_END = 2
from types import ListType
import __builtin__
from _Enum import Enum
from os.path import dirname,basename
import urlparse
from urllib2 import URLError
try:
	from xdg import Mime
except ImportError:
	Mime = None
try:
	import magic
except ImportError: # no magic
	magic = None
try:
	from os import popen
except ImportError: # occurs on Google AppEngine
	popen = None

try:
	import hashlib
except ImportError: # python < 2.5
	import md5
	hashlib = None

def hexdigest_md5(data):
	if hashlib:
		return hashlib.md5(data).hexdigest()
	else:
		return md5.new(data).hexdigest()

class URLTimeoutError(Exception):
	def __init__(self,string,url, code = -1):
		Exception.__init__(self,"%s - %s"%(string,url))
		self.url = url
		self.code = code

class URLHeaders:
	def __init__(self,headers, debug = False):
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
			raise KeyError, "No content type header!"
		if type(ct) == ListType:
			good = None
			for x in ct:
				if good:
					assert x == good,(x,ct, self.headers)
				elif x.find("/")!=-1:
					good = x
			ct = good
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
		if type(self.headers["Set-Cookie"]) == ListType:
			hdrs = self.headers["Set-Cookie"]
		else:
			hdrs = [self.headers["Set-Cookie"]]
		return dict([x.split(";")[0].split("=",1) for x in hdrs])
	
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
	def __init__(self,url,ref,data,headers={},postData=None):
		self.url = url
		self.data = data
		self.ref = ref
		self.headers = URLHeaders(headers)
		self.location = 0
		self.postData = postData
		
		if data!=None and headers!={}:
			try:
				mime = self.getmime()
			except KeyError:
				return
			if mime[0] !="image":
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

	def hash(self):
		return URLObject.md5(self.url, self.ref, self.postData)

	@staticmethod
	def md5(url,ref,data):
		return hexdigest_md5(url.decode("ascii","ignore")+str(ref)+str(data))

class URLGetter:
	def __init__(self,debug = False):
		self.timeout = 40
		self.debug = debug
		
	def setTimeout(self, val):
		self.timeout = val
	
	def getTimeout(self):
		return self.timeout

	def auth(self,user,password):
		raise Exception, "%s has not defined auth"%self.__class__

	def get(self,*args):
		raise Exception, "%s has not defined get"%self.__class__

	get_args = ('headers','proxy','ref','ignore_move')

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
					raise URLTimeoutError,("301/302/303, but no location!",url,status)
				revised = urljoin(url,newuri)
				if revised == kwargs['url']:
					print "status", status
					print "kwargs", kwargs
					raise Exception, "matched at %s"%revised
				print "revised", revised, kwargs['url']
				del kwargs['url']
				del kwargs['self']
				return self.get(revised, **kwargs)

			except:
				print "info",info
				raise
		return None

	def gen_headers(self, hdrs):
		info = {}
		for hdr in hdrs:
			if hdr == "":
				continue
			try:
				(type,data) = hdr.split(':',1)
			except:
				print "header was %s"%hdr
				raise
			temp = data[1:]
			while (len(temp)>0 and (temp[-1]=='\r' or temp[-1]=='\n')):
				temp =temp[:-1]
			if len(temp)==0:
				continue
			if info.has_key(type):
				if __builtin__.type(info[type])!=ListType:
					old = info[type]
					info[type] =[old]
				info[type].append(temp)
			else:
				info[type] = temp
		return info

class URLPython:
	def __init__(self,url,debug=False):
		if debug:
			print "made urlpython"
		self._url = url
		cmd = "cd %s;python %s"%(dirname(url),basename(url))
		print "cmd",cmd
		if popen == None:
			raise Exception, "Don't have popen!"
		data = popen(cmd,"r").readlines()
		self.msg = URLHeaders({})
		self.status = 200
		self.body = "".join(data[2:])

def get_good_mime(filename):
	mime = None
	if Mime != None:
		mime = Mime.get_type_by_contents(filename)
	if mime == None: # try magic instead
		if magic!=None:
			mime = magic.open(magic.MAGIC_MIME)
			mime.load()
			mime = mime.file(filename)
			mime = mime.split(";")[0]
	else:
		mime = str(mime)
	return mime

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
		self.msg.headers["Content-type"] = get_good_mime(url)
		self.status = 200

class Kind(Enum):
	http=1
	file=2
	python=3
	https=4

def handleurl(url):
	if url == "":
		raise URLError, "Need a URL!"
	bits = urlparse.urlsplit(url)
	rest ="".join(bits[1:])
	while len(rest)>0 and rest[0]=="/":
		rest = rest[1:]
	try:
		mykind = Kind.valid(bits[0])
	except ValueError:
		raise URLError, "'%s' isn't a valid URL!"%url

	#print "kind",url,mykind,rest
	if mykind == Kind.file:
		return URLFile(rest)
	elif mykind == Kind.python:
		return URLPython(rest)
	elif mykind == Kind.http or mykind == Kind.https:
		return None
	else:
		raise Exception, mykind
	
