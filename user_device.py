import datetime
import platform

import wmi

WMI = wmi.WMI()

def format_date(date):
    return datetime.strptime(date[:8], '%Y%m%d%H%')

class OperatingSystemInfo:
    def os_info(self):
        return platform.uname()

    def user_os(self):
        os_info = self.os_info()
        os_name = os_info.system
        os_version = os_info.release
        os_bit_version = '32'
        if '64' in os_info.machine:
            os_bit_version = '64'
        return [os_name, os_version, os_bit_version]

class BaseBoard:
    def __init__(self):
        self.device = None

    def info(self):
        return self.set_device(WMI.Win32_BaseBoard()[0])

    def set_device(self, data):
        self.device = data
        return data

    def model(self):
        return self.device.Product

    def manufacturer(self):
        return self.device.Manufacturer

class Chipset:
    def __init__(self):
        self.device = None

    def processor_info(self):
        return WMI.Win32_Processor()[0]

    def processor_name(self):
        processor = self.processor_info()
        if processor.Manufacturer == 'AuthenticAMD':
            caption = 'AMD_Chipset_Drivers'
        elif processor.Manufacturer == 'GenuineIntel':
            caption = 'Intel(R) Chipset Device Software'
        return caption

    def info(self):
        processor = self.processor_name()
        return self.set_device(WMI.Win32_Product(caption=processor)[0])

    def set_device(self, data):
        self.device = data
        return data

    def name(self):
        return self.device.Name.replace('_', ' ')

    def version(self):
            return self.device.Version

class BIOS:
    def __init__(self):
        self.device = None

    def info(self):
        data = WMI.Win32_BIOS()[0]
        return self.set_device(data)

    def set_device(self, data):
        self.device = data
        return data

    def name(self):
        return 'BIOS'

    def version(self):
        return self.device.SMBIOSBIOSVersion

    def release_date(self):
        return format_date(self.device.ReleaseDate)

class BoardLAN:
    # Detects all network LAN adapters in user's system
    def lan_adapters(self):
        wql = "SELECT * FROM Win32_NetworkAdapter WHERE NetConnectionID LIKE 'Ethernet%' and PNPDeviceID LIKE 'PCI%'"
        return WMI.query(wql)   

class LAN:
    def __init__(self):
        self.device = None

    def info(self):
        data = WMI.Win32_PnpSignedDriver(deviceclass='NET', devicename=self.device.ProductName)[0]
        return self.set_device(data)

    def set_device(self, data):
        self.device = data
        return data

    def name(self):
        return self.device.DeviceName

    def version(self):
        return self.device.DriverVersion
        
    def release_date(self):
        return format_date(self.device.DriverDate)

class Audio:
    def __init__(self):
        self.device = None

    def board_audio(self):
        return WMI.Win32_SoundDevice()[0]

    def info(self):
        sound_device = self.board_audio()
        data = WMI.Win32_PnpSignedDriver(deviceclass='MEDIA', devicename=sound_device.Name)[0]
        return self.set_device(data)

    def set_device(self, data):
        self.device = data
        return data

    def name(self):
        return self.device.DeviceName

    def version(self):
        return self.device.DriverVersion

    def release_date(self):
        return format_date(self.device.DriverDate)

class VGA:
    def __init__(self):
        self.device = None

    def info(self):
        for vga in WMI.Win32_VideoController(adapterdactype='Internal'):
            return self.set_device(vga)

    def set_device(self, data):
        self.device = data
        return data

    def name(self):
        return self.device.Name

    def version(self):
        if self.device:
            return self.device.DriverVersion
        return None

    def release_date(self):
        if self.device:
            return format_date(self.device.DriverDate)
        return None

class WiFi:
    def __init__(self):
        self.device = None

    def board_wifi(self):
        for wifi in WMI.Win32_NetworkAdapter(netconnectionid='Wi-Fi'):
            return wifi

    def info(self):
        board_wifi = self.board_wifi()
        if board_wifi:
            for wifi in WMI.Win32_PnpSignedDriver(deviceclass='NET', devicename=board_wifi.ProductName):
                return self.set_device(wifi)
        return None

    def set_device(self, data):
        self.device = data
        return data

    def name(self):
        return self.device.DeviceName

    def version(self):
        if self.wifi:
            return self.device.DriverVersion
        return None

    def release_date(self):
        if self.device:
            return format_date(self.device.DriverDate)

class Bluetooth:
    def __init__(self):
        self.device = None

    def info(self):
        for bluetooth in WMI.Win32_PnpSignedDriver(deviceclass='BLUETOOTH'):
            return self.set_device(bluetooth)
        return None

    def set_device(self, data):
        self.device = data
        return data

    def name(self):
        return self.device.DeviceName

    def version(self):
        if self.device:
            return self.device.DriverVersion
        return None

    def release_date(self):
        if self.device:
            return format_date(self.device.DriverDate)
        return None

def find_driver_class(driver):
        driver_class = {
            'bios': BIOS(),
            'lan' : LAN(),
            'audio': Audio(),
            'chipset': Chipset(),
            'vga': VGA(),
            'wifi': WiFi(),
            'bluetooth': Bluetooth()
        }
        return driver_class.get(driver)
