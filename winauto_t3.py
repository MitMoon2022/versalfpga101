from pywinauto import Application, keyboard, mouse
import time
from pywinauto.timings import Timings

# Start the application C:\Program Files (x86)\Mobile Centrality Tester\
app = Application().start(
    r"C:\Program Files (x86)\Mobile Centrality Tester\Mobile Centrality Tester_SGP.exe")
app = Application().connect(title_re="Mobile Centrality Tester.*", class_name="LVDChild", timeout=5)  # in sec
window = app.LVDChild
window.set_focus()
# Send the "Enter" keystroke
keyboard.send_keys('{ENTER}')
window.print_control_identifiers()
# -- 7/23 --
window.Maximize()
time.sleep(2)
# Get the current mouse position
# current_position = mouse.get_position()
# print(f"Current mouse position: {current_position}")

mouse.click('left', (95, 349))  # text box given for infor. Handler ID
keyboard.send_keys('SLT4-TrolleyR')
time.sleep(1)
mouse.click('left', (85, 426))  # text box given for infor. DUT/SITE
keyboard.send_keys('SV60_S5_23gf')
time.sleep(1)
mouse.click('left', (183, 522))  # Click to start Acquire!

# click on Tare
time.sleep(1)
#mouse.click('left', (231, 589))  # Click to start Tare button!
mouse.double_click('left', (231, 589)) # Click to start Tare button!
# Sleep for 5 sec
time.sleep(5)       #
# app.kill()
# Activate Plunger down
# Sleep for 30sec - wait for the reading to be stable.
time.sleep(1)       # vary this value until the reading is stable.
mouse.click('left', (176, 645))  # Click to stop!

# screenshot the result.
time.sleep(2)
mouse.click('left', (176, 827))  # Click to screenshot!
# To be defined whether to stop/kill the process or not.
time.sleep(2)
keyboard.send_keys('SShot_test1')
time.sleep(2)
keyboard.send_keys('{ENTER}')
time.sleep(2)