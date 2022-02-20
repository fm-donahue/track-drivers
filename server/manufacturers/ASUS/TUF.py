from ASUS import ASUS

class TUF(ASUS):
    def __init__(self, model, os_info):
        super().__init__(model, os_info)
        model_list = model.split()
        self.product_series = "-".join(model_list[:2])
        self.url = f'/Motherboards-Components/Motherboards/{self.product_series}/{"-".join(model_list)}/HelpDesk_Download/'