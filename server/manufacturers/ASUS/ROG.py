from ASUS import ASUS
import time
import requests
import random
from bs4 import BeautifulSoup
import re

class ROG(ASUS):
    def __init__(self, model, os_info):
        super().__init__(model, os_info)
        self.host = 'https://rog.asus.com'
        model_list = model.split()
        self.url = f'/motherboards/{"-".join(model_list[:2])}/{"-".join(model_list)}/helpdesk_download'
        self.api_url = '/support/webapi/product'
        
class RequestProductInfoROGByAPI:
    def __init__(self, series):
        self.series = series
        self.request_success = False

    def product_info(self):
        url_filename = '/api/v1/route/info?weburl='
        results = requests.get(self.series.host + url_filename + self.series.url, params=self.series.params, headers=self.series.headers).json()
        if results['Status'] != '0':
            self.request_success = False
        self.series.add_params(pdid = results['Result']['ProductID'])
        self.series.add_params(leveltagid = results['Result']['LevelTagID'])
        self.request_success = True
        time.sleep(random.inform(5, 10))

class RequestProductInfoROGByHTML:
    def __init__(self, series):
        self.series = series
        self.url_response = self.request_url()

    def request_url(self):
        data = requests.get(self.series.host + self.series.url, headers=self.series.headers).content
        time.sleep(random.inform(5, 10))
        return data

    def product_info(self, param, name):
        soup = BeautifulSoup(self.url_response, 'lxml')
        script = soup.find('script', text=re.compile(r'{}=[0-9]+'.format(name)))
        pd_obj = re.search(r'{}="(.*?)"'.format(name), script.string)
        pd_data = pd_obj.group(0).split('=')
        return self.series.add_params(**{f'{param}': f'{pd_data[1]}'})

# class ROGDrivers(ProductSeries):
#     def __init__(self, model, info):
#         self.series_info = ROG(model, info)

#     def request_product_info(self):
#         product = RequestProductInfoROGByAPI(self.series_info)
#         product.product_info()
#         if product.request_success == False:
#             product = RequestProductInfoROGByHTML(self.series_info)
#             product.product_info('pdid', 'ProductID')
#             product.product_info('leveltagid', 'LevelTagID')
