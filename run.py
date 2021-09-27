#!DriverTracker/.venv/Scripts/python

from track_drivers import Application

if __name__ == '__main__':
    print('Tracking drivers. . .')
    tracker = Application()
    tracker.run()
    print('Tracking completed. . .')