import psutil
import time
import threading
from PIL import Image
import pystray
from pystray import MenuItem as item
import io
import sys
import os
import winreg
import base64
import msvcrt


##Devpy.ir / Dev-py.ir / art_yasina


def ensure_single_instance():
    lock_file = os.path.join(os.getenv('TEMP'), 'SpeedNetTray.lock')
    global lock_handle
    lock_handle = open(lock_file, 'w')
    try:
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
    except IOError:
        print("Another instance is already running.")
        sys.exit()


# آیکون tray معتبر به صورت base64 (فرمت PNG)
ICON_BASE64 = "AAABAAEAGBgAAAEAIACICQAAFgAAACgAAAAYAAAAMAAAAAEAIAAAAAAAAAkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8o////rf///ygAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yj////n/////////+f///8oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////KP///+f////7//////////v////n////KAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8m////5f///+n///9r/////////2b////l////6P///ysAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////KgAAAAAAAAAAAAAAAP///yj////n////5////yj///9A/////////0D///8o////5////+f///8oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///82/////////zYAAAAAAAAAAP///6z////n////KAAAAAD///9A/////////0AAAAAA////KP///+f///+sAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAP///xX///8WAAAAAAAAAAD///9A/////////0AAAAAAAAAAAP///xb///8VAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///xX///8WAAAAAAAAAAD///9A/////////0AAAAAAAAAAAP///xb///8VAAAAAAAAAAD///9A/////////0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///6z////n////KAAAAAD///9A/////////0AAAAAA////KP///+f///+sAAAAAAAAAAD///82/////////zYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yj////n////5////yj///9A/////////0D///8o////5////+f///8oAAAAAAAAAAAAAAAA////KgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8n////5f///+j///9q/////////2b////l////6f///ysAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////KP///+f////7//////////v////n////KAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yj////n/////////+f///8oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8o////rf///ygAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8A////AP/+PwD//B8A//gPAP/wBwD+4AMA/GIjAPxmMwD8fj8A/H4/APx+PwD8fj8A/H4/APx+PwDMZj8AxEY/AMAHfwDgD/8A8B//APg//wD8f/8A////AP///wA="
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "SpeedNetTray"

def is_in_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ)
        _, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except:
        return False

def add_to_startup():
    path = os.path.abspath(sys.argv[0])
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, path)
    winreg.CloseKey(key)

def remove_from_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass

class NetSpeedTray:
    def __init__(self):
        image_data = base64.b64decode(ICON_BASE64)
        image = Image.open(io.BytesIO(image_data))
        self.startup_enabled = is_in_startup()

        self.icon = pystray.Icon("SpeedNet", image, "net Speed ", menu=pystray.Menu(
            item("Add Startup", self.enable_startup, enabled=lambda item: not self.startup_enabled),
            item("Remove Startup", self.disable_startup, enabled=lambda item: self.startup_enabled),
            item("Exit", self.quit)
        ))

        counters = psutil.net_io_counters()
        self.last_upload = counters.bytes_sent
        self.last_download = counters.bytes_recv

        self.running = True
        self.thread = threading.Thread(target=self.update_speed)
        self.thread.daemon = True
        self.thread.start()

    def enable_startup(self):
        add_to_startup()
        self.startup_enabled = True
        self.icon.update_menu()

    def disable_startup(self):
        remove_from_startup()
        self.startup_enabled = False
        self.icon.update_menu()

    def update_speed(self):
        while self.running:
            time.sleep(1)
            counters = psutil.net_io_counters()
            upload = (counters.bytes_sent - self.last_upload) * 8 / 1024  # Kbps
            download = (counters.bytes_recv - self.last_download) * 8 / 1024  # Kbps
            self.last_upload = counters.bytes_sent
            self.last_download = counters.bytes_recv
            self.icon.title = f"⬇ {download:.1f} Kbps\n⬆ {upload:.1f} Kbps"


    def quit(self, icon=None, item=None):
        self.running = False
        self.icon.stop()

    def run(self):
        self.icon.run()

if __name__ == "__main__":
    ensure_single_instance()
    tray = NetSpeedTray()
    tray.run()

