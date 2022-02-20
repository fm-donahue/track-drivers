import requests

class ServerApplicationError(Exception):
    code = 500
    description = 'Server Error'

class ParseAttributeError(ServerApplicationError):
    pass

class ResponseFail(ServerApplicationError):
    pass

class UrlRedirected(ServerApplicationError):
    pass

class ServerRequestsError(requests.exceptions.RequestException):
    code = 500
    description = 'Server Requests Error'
