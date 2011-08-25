#!/usr/bin/python
# Cache module by Tom Parker <palfrey@tevp.net>
# http://tevp.net/
#
# Released under the GPL Version 2 (http://www.gnu.org/copyleft/gpl.html)
import os,time,sys
from cPickle import dump,load,UnpicklingError
from _URLTimeout import URLTimeout
from _URLTimeoutCommon import URLTimeoutError, URLObject
from stat import ST_MTIME
import copy

try:
	from google.appengine.api import memcache
except ImportError:
	memcache = None

class URLOldDataError(Exception):
	pass

class Cache:
	def __init__(self,cache="cache", debug=False):
		self.cache = cache
		self.store = {}
		self.debug = debug
		self.grabber = URLTimeout(debug)
		self.default_timeout = self.grabber.getTimeout()
		if memcache == None and not os.path.exists(cache):
			os.mkdir(cache)

	def __load__(self,url,ref, data = None):
		hash = URLObject.md5(url,ref,data)
		if self.store.has_key(hash):
			return
		if memcache:
			get = memcache.get(hash)
			if get != None:
				self.store[hash] = get
			return
		f = hash+".cache"
		if f in os.listdir(self.cache):
			try:
				if self.debug:
					print "loading",os.path.join(self.cache,f)
				old = load(file(os.path.join(self.cache,f)))
				old.seek(0)
				if len(old.readall())==0:
					raise EOFError()
				self.store[old.hash()] = old
				if self.debug:
					print "loaded",old.url,old.ref,old.hash()
				if(old.hash()!=f[:-len(".cache")]):
					raise Exception,"md5 problem!"
			except (EOFError,ValueError,UnpicklingError,ImportError): # ignore and discard				
				if self.debug:
					print "discarded",f,sys.exc_info()
				os.unlink(os.path.join(self.cache,f))
	
	def auth(self,user,password):
		self.grabber.auth(user,password)

	def _dump(self,url,ref,data):
		self.__load__(url,ref,data)
		hash = URLObject.md5(url,ref,data)

		if self.store.has_key(hash):
			if self.debug:
				print "dumping",url,ref,hash
			if memcache!=None:
				memcache.set(hash, self.store[hash])
			else:
				f = file(os.path.join(self.cache,hash+".cache"),'wb')
				dump(self.store[hash],f)
				f.close()
		else:
			raise Exception, "We never got that URL! ("+url+")"
	
	user_agent = None
	
	def get(self,url,ref=None, max_age=3600, data = None,headers={}, timeout=None): # 3600 seconds = 60 minutes
		if timeout == None:
			timeout = self.default_timeout
		if self.debug:
			print "Grabbing",url
		self.__load__(url,ref)
		hash = URLObject.md5(url,ref,data)
		if self.user_agent!=None:
			headers["User-Agent"] = self.user_agent
		now = time.time()
		if self.store.has_key(hash):
			old = self.store[hash]
			if self.debug:
				print "time diff",time.time()-old.checked
			if len(old.headers.headers)>0: # non-local file
				if max_age==-1 or now-old.checked < max_age:
					old.seek(0)
					old.used = now
					self._dump(old.url,old.ref,old.postData)
					return old

				if old.info().get("Last-Modified")!=None:
					headers["If-Modified-Since"] = old.info().get("Last-Modified")
				if old.info().get("ETag")!=None:
					headers["If-None-Match"] = old.info().get("ETag")
			else:
				try:
					if os.stat(url[len("file://"):])[ST_MTIME] <= old.checked:
						old.checked = old.used = now
						self._dump(old.url,old.ref,old.postData)
						return old
				except OSError,e:
					raise URLTimeoutError, (str(e),url)
		else:
			old = None
	
		self.grabber.setTimeout(timeout)

		try:
			new_old = self.grabber.get(url,ref=ref,headers=headers,data=data)
		except URLOldDataError:
			old.used = now
			old.seek(0)
			self._dump(old.url,old.ref,old.postData)
			return old

		old = new_old
		hash = old.hash()
		self.store[hash] = old
		old.checked = old.used = now
		old.seek(0)
		if old.url!=url:
			if self.debug:
				print "url != old.url, so storing both"
			other = copy.copy(old)
			other.url = url
			other.ref = ref
			hash = other.hash()
			self.store[hash] = other
			other.checked = other.used = now
			
		if len(old.headers.headers)>0:
			self._dump(old.url,old.ref,old.postData)
			if old.url!=url:
				self._dump(url,ref,data)
		if self.debug:
			print "Grabbed",old.url,old.ref
		return old
	
	def delete(self, obj): # removes from cache
		hash = obj.hash()

		if self.store.has_key(hash):
			if self.debug:
				print "deleting",obj.url,obj.ref,hash
			if memcache!=None:
				memcache.delete(hash)
			else:
				path = os.path.join(self.cache,hash+".cache")
				if os.path.exists(path):
					os.unlink(path)
			del self.store[hash]

		else:
			raise Exception, "We never got that URL! ("+obj.url+")"
	
	def urlretrieve(self, url, fname):
		try:
			obj = self.get(url)
		except URLTimeoutError:
			return False
		file(fname, "wb").write(obj.read())
		self.delete(obj)
		return True

if __name__ == "__main__":
	c = Cache(debug=True)
	t = time.time()
	for x in c.store.keys():
		o = c.store[x]
		if not o.__dict__.has_key("used") or t-o.used>72*60*60:
			try:
				os.unlink(os.path.join(c.cache,x+".cache"))
				print "dropped",x
			except:
				print "can't drop",x,o.url,o.ref
		else:
			print "age",t-o.used,o.url
