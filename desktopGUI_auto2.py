# https://www.youtube.com/watch?v=AELS18jVXhA

import time
from pywinauto import Application, keyboard
from pywinauto.timings import Timings

# Start the application C:\Program Files (x86)\Mobile Centrality Tester\
app = Application().start(r"C:\Program Files\PuTTY\putty.exe")
time.sleep(5)
app = Application().connect(title="PuTTY Configuration")  # in sec
window = app.PuTTYConfigBox
# window = app.PuttyConfiguration
window.set_focus()
window[u"Host Name (or IP address):Edit"].type_keys("172.22.22.5")
window[u"Port:Edit"].type_keys("23")
window["Open"].click()

