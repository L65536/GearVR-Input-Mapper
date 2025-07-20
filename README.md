# Introduction
This project is about custom mapping of a Samsung GearVR controller into simulated keyboard or mouse inputs.
The Python codes are presented in less than 200 lines and contains examples of input mappings. 
- Text interface with debug info display.
- Mapping of touchpad into 4+1 keys.
- Mapping of all other keys
- Multiple target window support with title matching 
- No gyro or accelerometer implemented here.

# Trouble shooting

System wide hotkey mapping often works with a single pyautogui.press() call. For example:
```
pyautogui.press('volumemute') 
pyautogui.press('volumeup') 
pyautogui.press('volumedown')
```
However sometimes mapped inputs of pyautogui are not detected by the target app/game.
keyDown()/sleep/keyUp() combo may be necessary when using pyautogui.
```
HOLD = 0.03
KEY = 'f12'

pyautogui.keyDown(KEY)
time.sleep(HOLD)
pyautogui.keyUp(KEY)  

pyautogui.mouseDown(button='right')
pyautogui.sleep(HOLD)
pyautogui.mouseUp(button='right')
```

# Acknowledgement and special thanks
The core of his project contains codes based on the following projects/libraries:
- https://jsyang.ca/hacks/gear-vr-rev-eng/
- https://github.com/BasselMalek/GearVR-controller-win10
- https://github.com/uutzinger/gearVRC
- https://github.com/hbldh/bleak
