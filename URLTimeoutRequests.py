import requests
from ._URLTimeoutCommon import *

class URLTimeoutRequests(URLGetter):
    def get(self, url, headers={}, ref=None, data=None, ignore_move=False, proxy=None):
        r = requests.get(url, headers)

        if r.status_code == 304:
            raise URLOldDataError

        if r.status_code != 200:
            raise URLTimeoutError(str(status[0])+" "+status[1],url, status[0])

        return URLObject(url, None, r.content, r.headers, data)
