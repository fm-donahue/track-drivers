from .ASUS import ASUS, RequestDrivers
from .Prime import Prime, PrimeUrlParameters


def identify_series(model, os_info):
        if 'prime' in model.lower():
            series = Prime(model, os_info)
            return series, PrimeUrlParameters(series)
        return ASUS(model, os_info)

class GetASUSDrivers:
    """This class runs all other ASUS class needed to get the drivers from their website"""

    def __init__(self, model, os_info, session):
        self.series, self.url_params = identify_series(model, os_info)
        self.session = session
        
    def run_drivers(self):
        self.session.headers.update(self.series.headers)
        self.session.params.update(self.series.params)
        self.url_params.set_session(self.session)
        self.url_params.get_product_ids()
        self.url_params.get_os_id()
        drivers = RequestDrivers(self.series, self.session)
        drivers.request_drivers()
        drivers.request_bios()
        return drivers

    def get_session(self):
        return self.session
