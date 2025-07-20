import time
import asyncio # pip install asyncio
from bleak import BleakClient # pip install bleak
from enum import Enum
import pyautogui
pyautogui.FAILSAFE = False

import win32gui # pip install pywin32
from win32.win32gui import FindWindow, GetWindowRect, GetForegroundWindow, GetWindowText

address = "2C:BA:BA:2F:46:93" # USE YOUR OWN DEVICE ADDRESS HERE <<<<<=====
MODEL_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
INFO_UUID = "C8C51726-81BC-483B-A052-F7A14EA3D281"
COMMAND_UUID = "C8C51726-81BC-483B-A052-F7A14EA3D282"
battery_level_characteristic = '00002a19-0000-1000-8000-00805f9b34fb'

class Modes(Enum):
    No_Comm = 0x0000
    Normal_Comm = 0x0100
    VR_Comm = 0x0800

touched=0 # flag for tracking individual touches
count=0 # debug counter for testing individual touches
HOLD=0.03 # hold time for key press
MAX=315 # touch pad effective range
EDGE=50 # touch pad user defined effective region
lastX=0 # tracking coordinates for mouse mode
lastY=0 # tracking coordinates for mouse mode
detected_titles=[] # active window title lists
TITLE1='Notepad' # foreground window title for partial matching
TITLE2='xxx' # foreground window title for partial matching

async def cantusenotify(client, INFO_UUID):
    while True:
        global touched
        global count        
        global last_title
        global lastX, lastY
        data = await client.read_gatt_char(INFO_UUID) # VR mode, 30 ms report rate
        axisX = (((data[54] & 0xF) << 6) +((data[55] & 0xFC) >> 2))
        axisY = (((data[55] & 0x3) << 8) +((data[56] & 0xFF) >> 0))
        # [TEST] pyautogui.moveTo((axisX*6.095*2),(axisY*3.428*2)) # 4K 2160p mouse mapping (absolute coordinate mode)
        # [TEST] pyautogui.moveTo((axisX*6.095),(axisY*3.428)) # FHD 1080p mouse mapping (absolute coordinate mode)

        # [DEBUG] Terminal display
        triggerButton    = "T" if ((data[58] &  1) ==  1) else "."
        homeButton       = "H" if ((data[58] &  2) ==  2) else "."
        backButton       = "B" if ((data[58] &  4) ==  4) else "."
        touchpadButton   = "C" if ((data[58] &  8) ==  8) else "."
        volumeUpButton   = "+" if ((data[58] & 16) == 16) else "."
        volumeDownButton = "-" if ((data[58] & 32) == 32) else "."
        print("\r(",axisX, axisY,"/315 )",triggerButton,homeButton,backButton,touchpadButton,volumeUpButton,volumeDownButton, "        ", end='')

        window_title = '+'
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            window_title = win32gui.GetWindowText(hwnd)
            if window_title not in detected_titles:
                if(len(window_title)>0):
                    print('\r', "Detected window title:", window_title)
                    detected_titles.append(window_title)

        # Global mouse mode (differential/relative/swipe mode)
        """
        if TITLE not in window_title:
            if(lastX!=0 and lastY !=0 and axisX!=0 and axisY!=0):
                pyautogui.move((axisX-lastX)*3,(axisY-lastY)*2)
            lastX=axisX
            lastY=axisY
            if ((data[58] &  1) ==  1): pyautogui.click(button='right') # Trigger Button
            if ((data[58] & 16) == 16): pyautogui.scroll(60) # "+"
            if ((data[58] & 32) == 32): pyautogui.scroll(-60) # "-"
            if ((data[58] &  8) ==  8): pyautogui.click() # Touchpad Button
        """

        # Per title key mapping # copy and modify this section for each app/game/title
        if TITLE1 in window_title:
        
            # Touchpad edge+centre mapped to 4+1 buttons
            if axisX==0 and axisY==0: touched=0 # reset touch
            if ((data[58] &  8) ==  8): touched=0 # reset touch when touchpad pressed
            if touched==0: # only process once per touch
                if axisX>0 or axisY>0:
                    touched=1 # only process once per touch
                    # count+=1 # tracking individaul touch count [DEBUG]

                    if axisY<EDGE: # UP
                        #pyautogui.scroll(1) 
                        KEY='up'
                        pyautogui.keyDown(KEY)
                        time.sleep(HOLD)
                        pyautogui.keyUp(KEY)
                    elif axisY>MAX-EDGE: # DOWN
                        #pyautogui.scroll(-1) 
                        KEY='down'
                        pyautogui.keyDown(KEY)
                        time.sleep(HOLD)
                        pyautogui.keyUp(KEY)
                    elif axisX<EDGE: # LEFT
                        #pyautogui.press('f1') 
                        KEY='f1'
                        pyautogui.keyDown(KEY)
                        time.sleep(HOLD)
                        pyautogui.keyUp(KEY)
                    elif axisX>MAX-EDGE: # RIGHT                    
                        pyautogui.mouseDown(button='right')
                        pyautogui.sleep(HOLD)
                        pyautogui.mouseUp(button='right')
                    else: pyautogui.scroll(-1) # Scroll Down # CENTRE

            # Key mapping
            if ((data[58] &  1) ==  1): # Trigger Button
                # pyautogui.press('f12')                
                KEY='f12'
                pyautogui.keyDown(KEY)
                time.sleep(HOLD)
                pyautogui.keyUp(KEY)
                
            #if ((data[58] &  2) ==  2): pyautogui.hotkey('alt', 'enter')   # Home Button
            if ((data[58] &  2) ==  2): pyautogui.hotkey('win', 'shift', 'z')   # Home Button
            if ((data[58] &  4) ==  4): pyautogui.press('volumemute') # Back Button
            if ((data[58] & 16) == 16): pyautogui.press('volumeup')   # volumeUpButton   = "+" repeat
            if ((data[58] & 32) == 32): pyautogui.press('volumedown') # volumeDownButton = "-" repeat
            #if ((data[58] &  8) ==  8): pyautogui.press('C') # Touchpad Button

async def run(address):
    async with BleakClient(address) as client:
        await client.write_gatt_char(COMMAND_UUID, bytearray.fromhex("0800"), response = True) # VR mode, 30 ms report rate, NEED BOTH MODE ON
        await client.write_gatt_char(COMMAND_UUID, bytearray.fromhex("0100"), response = True) # Sensor mode, slow 200-2000 ms, NEED BOTH MODE ON

        model_number = await client.read_gatt_char(MODEL_UUID)
        current_mode = await client.read_gatt_char(COMMAND_UUID)
        battery = await client.read_gatt_char(battery_level_characteristic)
        print("Model: {0} ".format("".join(map(chr,model_number))))
        print("Mode: {0} ({1})".format("".join(current_mode.hex()), Modes(int("0x" + current_mode.hex(), base=16)).name))
        print("Battery: ", int.from_bytes(battery, 'big'))        
        
        await cantusenotify(client, INFO_UUID)

asyncio.run(run(address))
