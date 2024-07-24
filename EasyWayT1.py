import pywinauto
from pywinauto import keyboard


#from pywinauto import Application, keyboard

pwa_app = pywinauto.application.Application().start(
    r"C:\Program Files (x86)\Mobile Centrality Tester\Mobile Centrality Tester_SGP.exe")
w_handle = pywinauto.findwindows.find_windows(title=u'Mobile Centrality Tester V1.0.1', class_name='LVDChild')
window = pwa_app.window_(handle=w_handle)
# window.ClickInput()

# Send the "Enter" keystroke
keyboard.send_keys('{ENTER}')





