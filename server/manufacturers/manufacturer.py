class ManufacturerInfo:
    def __init__(self, model, os_info):
        self.os_info = os_info
        self.model = model

    def add_headers(self, **kwargs):
        for key, value in kwargs.items():
            self.headers[key] = value

    def set_params(self, **kwargs):
        self.params = {}
        self.add_params(**kwargs)

    def add_params(self, **kwargs):
        for key, value in kwargs.items():
            self.params[key] = value

    def add_drivers(self, driver, *args):
        if driver:
            self.latest_drivers[driver] = []
        for driver in args:
            self.latest_drivers[driver] = []

    def set_url(self, url):
        self.url = url

    def driver_format_dict(self, name, version, release_date, download_url):
        return {'Name': name, 'Version': version, 'ReleaseDate': release_date,
                'DownloadURL': download_url}

