import re
import sys
from datetime import datetime

from manufacturers.manufacturer import ManufacturerInfo
from bs4 import BeautifulSoup
from request_helpers import random_user_agent, sleep_after_request, ResponseFail


def headers():
    return {
        'user-agent': random_user_agent()
    }

def params(model):
        return {
            'model': model.replace(' ', '-'),
            'cpu': '',
        }

class VerifyProductUrl:
    """Test url to find the correct url of the product"""

    def __init__(self, series, session):
        self.series = series
        self.session = session

    def test_url(self):
        url = self.series.host + self.series.url
        if self.url_status(url) == False:
            url = self.series.host + f'/supportonly/{self.series.model}/helpdesk_download' # Url of old asus board products
            if self.url_status(url) == True:
                return url

    @sleep_after_request(5, 10)
    def url_status(self, url):
        r = self.session.get(url, allow_redirects=False)
        if r.status_code == 200:
            return True
        return False

class RequestProductInfoByHTML:
    """Requests product details by using html data needed for parameters in requesting drivers"""

    def __init__(self, series, session):
        self.series = series
        self.session = session
        self.url_response = self.request_url()

    @sleep_after_request(5, 10)
    def request_url(self):
        results = self.session.get(self.series.host + self.series.url)
        return results

    def product_hashed_id(self):
        soup = BeautifulSoup(self.url_response.content, 'lxml')
        try:
            script = soup.find('script', text=re.compile(r'ProductHashedID:(.*?),'))
        except AttributeError as e:
            sys.exit('ProductHashedID not found on the page.' + e)

        re_group = re.search(r'ProductHashedID:"(.*?)"', script.string)
        _, value = re_group.group(0).split(':')
        id = re.sub('[^a-zA-Z0-9]', '', value)
        return id

    def product_id(self):
        soup = BeautifulSoup(self.url_response.content, 'lxml')
        try:
            script = soup.find('script', text=re.compile(r'"sku": [0-9]+'))
        except AttributeError as e:
            sys.exit('ProductID not found on the page.' + e)

        re_group = re.search(r'"sku": [0-9]+', script.string)
        _, value = re_group.group(0).split(':')
        id = re.sub('[^0-9]', '', value)
        return id

    def product_info(self):
        return self.product_hashed_id(), self.product_id()

class RequestOSInfo:
    """Requests os id needed for parameters in requesting drivers"""

    def __init__(self, series, session):
        self.series = series
        self.session = session
        
    @sleep_after_request(5, 10)
    def os_id(self):
        params = {'website': 'global'}
        results = self.session.get(self.series.host + self.series.api_url + '/GetPDOS', params=params)
        results_json = results.json()
        if results_json['Result'] == None:
            raise ResponseFail('Empty "Result". No OS id found.')
        for os_id in results_json['Result']['Obj']:
            if os_id['Name'] == (' ').join(self.series.os_info) + '-bit':
                return os_id['Id']

class RequestUrlParameters:
    def __init__(self, series):
        self.series = series
        self.session = None

    def get_product_ids(self):
        pass

    def get_os_id(self):
        os = RequestOSInfo(self.series, self.session)
        os_id = os.os_id()
        self.session.params.update({'osid': os_id})

    def verify_url(self):
        verify = VerifyProductUrl(self.series, self.session)
        url = verify.test_url()
        if url:
            self.series.set_url = url
        return

    def set_session(self, session):
        self.session = session

class ASUSUrlParameters(RequestUrlParameters):
    def get_product_ids(self):
        self.verify_url()
        product = RequestProductInfoByHTML(self.series, self.session)
        product_hashed_id, product_id = product.product_info()
        self.session.params.update({'pdhashedid': product_hashed_id, 'pdid': product_id})

class RequestDrivers:
    def __init__(self, series, session):
        self.series = series
        self.session = session
        self.headers = {'referer': self.series.host + self.series.url}
        self.params = {'website': 'global'}
        self.drivers = {}

    @sleep_after_request(5, 10)
    def request_drivers(self):
        results = self.session.get(self.series.host + self.series.api_url + '/GetPDDrivers', headers=self.headers, params=self.params)
        results_json = results.json()
        if results_json['Status'] == 'FAIL':
            raise ResponseFail('Response does not contain any drivers. {}'.format(results.url))
        drivers = results_json['Result']['Obj']
        for driver in drivers:
            driver_lower = driver['Name'].lower()
            for idx, file in enumerate(driver['Files']):
                self.set_drivers(driver_lower, file)
                if driver_lower == 'lan' and idx < 1:
                    continue
                break

    @sleep_after_request(5, 10)
    def request_bios(self):
        results = self.session.get(self.series.host + self.series.api_url + '/GetPDBIOS', headers=self.headers, params=self.params)
        results_json = results.json()
        if results_json['Result'] == None:
            raise ResponseFail('Url response does not contain any bios drivers. {}'.format(results.url))
        bios_files = results_json['Result']['Obj'][0]['Files']
        for file in bios_files:
            if file['IsRelease'] == '1':
                self.set_drivers('bios', file)
                break

    def get_drivers(self):
        return self.drivers

    def set_drivers(self, driver, data):
        release_date = self.series.format_date(data['ReleaseDate'])
        driver_formatted = self.series.driver_format_dict(data['Title'], data['Version'], release_date, 
                                data['DownloadUrl']['Global'])
        if driver not in self.drivers:
            self.drivers[driver] = driver_formatted
            return
        update_driver = {driver: [self.drivers.get(driver), driver_formatted]}
        self.drivers.update(update_driver)

class ASUS(ManufacturerInfo):
    def __init__(self, model, os_info):
        super().__init__(model, os_info)
        self.headers = headers()
        self.params = params(model)
        self.host = 'https://www.asus.com'
        model_list = model.split()
        self.product_series = model_list[0]
        self.url = f'/Motherboards-Components/Motherboards/{self.product_series}/{"-".join(model_list)}/HelpDesk_Download/'
        self.api_url = '/support/api/product.asmx'

    def format_date(self, date):
        return datetime.strptime(date, '%Y/%m/%d')
                