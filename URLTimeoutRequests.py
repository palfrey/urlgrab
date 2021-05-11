import requests
from . import *

class URLTimeoutRequests(URLGetter):
    def get(self, url, headers={}, ref=None, data=None, ignore_move=False, proxy=None):
        try:
            if ref is not None:
                headers.update({'referer': ref})
            r = requests.get(url, headers=headers, verify=False)
        except Exception as e:
            raise URLTimeoutError(str(e), url)

        if r.status_code == 304:
            raise URLOldDataError

        if r.status_code != 200:
            raise URLTimeoutError(str(r.status_code) + " " + r.reason, url, r.status_code)
        
        if r.encoding == "UTF-8":
            return URLObject(url, ref, r.text, r.headers, data)
        else:
            return URLObject(url, ref, r.content, r.headers, data)
