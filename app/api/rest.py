import requests
from ..exceptions import ApiError

class Restful():
    def __init__(self):
        pass

    def _request(self, method, url, data, auth):
        response = None
        if data is None:
            try:
                response = requests.request(method, 
                                            url=url,
                                            auth=auth)
            except ApiError as err:
                print(err)
        else:
            try:
                response = requests.request(method, 
                                            url=url, 
                                            data=data, 
                                            headers={'Content-Type':'application/json'},
                                            auth=auth)
            except ApiError as err:
                print(err)
        return response

    def get(self, endpoint, data=None, auth=None):
        return self._request("get", endpoint, data, auth)

    def post(self, endpoint, data=None, auth=None):
        return self._request("post", endpoint, data, auth)

    def put(self, endpoint, data=None, auth=None):
        return self._request("put", endpoint, data, auth)

    def delete(self, endpoint, data=None, auth=None):
        return self._request("delete", endpoint, data, auth)