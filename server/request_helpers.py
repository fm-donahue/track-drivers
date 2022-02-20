import functools
import random
import time

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from errors import ServerRequestsError


def random_user_agent():
    user_agent = [
    #Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
    #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    #Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38'
    ]
    return random.choice(user_agent)

def sleep_after_request(tmin, tmax):
    def decorator(func):
        @functools.wraps(func)
        def wrapper_sleep_request(*args, **kwargs):
            value = func(*args, **kwargs)
            time.sleep(random.uniform(tmin, tmax))
            return value
        return wrapper_sleep_request
    return decorator


'''
The codes below are inspired by this online article:
https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
'''

def event_handling(s, *args, **kwargs):
    try:
        s.raise_for_status()

    except requests.exceptions.ConnectionError as e:
        raise ServerRequestsError('Connection Error', e.response) from e

    except requests.exceptions.HTTPError as e:
        raise ServerRequestsError('Http Error. Details given below', e.response) from e

    except requests.exceptions.Timeout as e:
        raise ServerRequestsError('Retry limit reached', e.response) from e

    except requests.exceptions.TooManyRedirects as e:
        raise ServerRequestsError('Bad url. Check and update url', e.response) from e

    except requests.exceptions.RequestException as e:
        raise ServerRequestsError('Something else happened.', e.response) from e

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs["timeout"]
        del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
    
def open_session(retries=5, timeout=5):
    retry_strategy = Retry(
        total = retries,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = TimeoutHTTPAdapter(max_retries=retry_strategy, timeout=timeout)
    s = requests.Session()
    s.mount('https://', adapter)
    s.mount('http://', adapter)
    s.hooks['response'] = [event_handling]
    return s
