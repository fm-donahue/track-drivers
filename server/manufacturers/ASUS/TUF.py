from ASUS import ASUS

class TUF(ASUS):
    def __init__(self, model, os_info):
        super().__init__(model, os_info)
        model_list = model.split()
        self.product_series = "-".join(model_list[:2])
        self.url = f'/Motherboards-Components/Motherboards/{self.product_series}/{"-".join(model_list)}/HelpDesk_Download/'

# class TUFDrivers(ProductSeries):
#     def __init__(self, model, info):
#         self.series_info = TUF(model, info)

#     def request_product_info(self):
#         product = RequestProductInfoByAPI(self.series_info)
#         product.product_info()
#         if product.request_success == False:
#             product = RequestProductInfoByHTML(self.series_info)
#             product.pdhashedid()
#             product.pdid()