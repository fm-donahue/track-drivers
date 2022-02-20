from manufacturers.ASUS.asus_helpers import GetASUSDrivers

def manufacturer_class(board_maker, model, os_info, session):
    if board_maker == 'ASUSTeK COMPUTER INC.':
        return GetASUSDrivers(model, os_info, session)
    raise NotImplementedError(f'Tracking drivers of {board_maker} manufacturer has not yet implemented.')
