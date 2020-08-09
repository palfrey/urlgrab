import requests
from ._URLTimeoutCommon import *

class URLTimeoutRequests(URLGetter):
    def get(self, url, headers={}, ref=None, data=None, ignore_move=False, proxy=None):
        try:
            r = requests.get(url, headers=headers)
        except Exception as e:
            raise URLTimeoutError(str(e), url)

        if r.status_code == 304:
            raise URLOldDataError

        if r.status_code != 200:
            raise URLTimeoutError(str(r.status_code), r.reason,url, r.status_code)

        return URLObject(url, None, r.content, r.headers, data)
