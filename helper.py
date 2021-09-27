from manufacturers.ASUS.asus_helpers import GetASUSDrivers

def manufacturer_class(board_maker, model, os_info):
    board_manufacturers = {
        'ASUSTeK COMPUTER INC.': GetASUSDrivers(model, os_info)
    }
    return_data = board_manufacturers.get(board_maker)
    if return_data:
        return return_data
    raise NotImplementedError(f'Tracking drivers of {board_maker} manufacturer has not yet implemented.')
