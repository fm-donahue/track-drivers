# Track Drivers

A Python script that notifies the user if a new driver is available and ready to download. The script compares the drivers in the user's system to drivers found on the manufacturer's website.

Note: This only works on ASUS Prime series motherboard.

## Dependencies

This script requires few library dependencies.

- [Requests](https://docs.python-requests.org/en/latest/)
- [WMI](https://pypi.org/project/WMI/)
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Win10toast_click](https://pypi.org/project/win10toast-click/)

## Installation
1. Clone the repository
```
git clone https://github.com/fm-donahue/track-drivers.git
cd track-drivers
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Then run script using:
```bash
python run.py
```

## License
[MIT](https://github.com/fm-donahue/track-drivers/blob/main/LICENSE)
