import os
import re
import time
from collections import deque

import requests
from win10toast_click import ToastNotifier

from helpers import get_request_drivers
from user_device import (BaseBoard, BoardLAN, OperatingSystemInfo,
                         find_driver_class)

SAVE_PATH = os.path.expanduser('~' + '/Downloads/')

class CompareDrivers:
    def compare_drivers(self, user_driver, web_driver):
        if user_driver.info():
            is_newer = self.new_version(user_driver, web_driver)
            if is_newer:
                web_driver['Title'] = user_driver.name()
                return web_driver

    def compare_lan_drivers(self, user_driver, web_driver):
        board_lan = BoardLAN()
        list_new_drivers = []
        lan_adapters = board_lan.lan_adapters()
        regex = re.compile(r'^\d*[.,]?\d*G[a-zA-Z]*')
        for idx in range(len(lan_adapters)):
            bandwidth = regex.search(web_driver[idx]['Name'])
            for lan in lan_adapters:
                if bandwidth and bandwidth.group() in lan.ProductName:
                    break
                elif not bandwidth and not regex.search(lan.ProductName):
                    break
            user_driver.set_device(lan)
            new_driver = self.compare_drivers(user_driver, web_driver[idx])
            if new_driver:
                list_new_drivers.append(new_driver)
        return list_new_drivers

    def new_version(self, user, web):
        split_user = user.version().split('.')
        split_web = web['Version'].split('.')
        for user_n, web_n in zip(split_user, split_web):
            # Check if both version has the same format, if not check by their release date
            if len(user_n) == len(web_n):
                if user_n < web_n:
                    return True
                elif user_n > web_n:
                    return False
            else:
                return self.new_by_date(user, web)

    def new_by_date(self, user, web):
        return user.release_date() < web['ReleaseDate']

class Notification:
    """
    Send notification to user (if new driver is available).
    Downloads the drivers by clicking the banner.
    """

    def __init__(self, toast):
        self.toaster = toast
        self.queue = deque()

    def notify_user(self):
        if not self.queue:
            self.toaster.show_toast(
                "This program determined that the best drivers",
                "are already installed.",
                duration=10,
                )
            return
        while self.queue:
            dequeue = self.queue.popleft()
            self.toaster.show_toast(
                f"{dequeue['Title']} {dequeue['Version']}",
                "Click to download the latest driver.",
                icon_path=None,
                duration=10,
                callback_on_click=lambda: self.download_driver(dequeue)
            )
        # Wait for threaded notification to finish
        while self.toaster.notification_active():
            time.sleep(0.1)

    def download_driver(self, data):
        dl_request = requests.get(data['DownloadURL'], stream=True)
        filename = f"{data['Title']} {data['Version']}"
        file = os.path.join(SAVE_PATH, filename + '.zip')
        with open(file, 'wb') as f:
            for chunk in dl_request.iter_content(chunk_size=128):
                f.write(chunk)

    def append_queue(self, data):
        self.queue.append(data)

class Application:
    def run(self):
        toast = ToastNotifier()
        compare = CompareDrivers()
        board = BaseBoard()
        board.info()
        operating_system = OperatingSystemInfo()
        web_drivers = get_request_drivers(board.manufacturer(), board.model(), operating_system.user_os())
        notify = Notification(toast)

        for driver, value in web_drivers.items():
            newer_driver = None
            user_driver = find_driver_class(driver)
            if user_driver:
                if driver != 'lan':
                    newer_driver = compare.compare_drivers(user_driver, value)
                    if newer_driver:
                        notify.append_queue(newer_driver)
                else:
                    newer_driver = compare.compare_lan_drivers(user_driver, value)
                    for driver in newer_driver:
                        notify.append_queue(driver)

        notify.notify_user() 
