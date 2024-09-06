# License: GPLv2.0
# Copyright (c) 2023 Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)

import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
import pwmio
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode
import logging
import analogio

# Duckyscript command dictionary
duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI, 'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 
    'SHIFT': Keycode.SHIFT, 'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL, 
    'DOWNARROW': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 
    'UPARROW': Keycode.UP_ARROW, 'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE, 
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'HOME': Keycode.HOME, 'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK,
    'PAGEUP': Keycode.PAGE_UP, 'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB, 'BACKSPACE': Keycode.BACKSPACE, 
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E, 'F': Keycode.F, 'G': Keycode.G,
    'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J, 'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 
    'O': Keycode.O, 'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T, 'U': Keycode.U, 
    'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y, 'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 
    'F3': Keycode.F3, 'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7, 'F8': Keycode.F8, 
    'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11, 'F12': Keycode.F12
}

# Convert lines in Duckyscript to keycodes
def convertLine(line):
    newline = []
    for key in filter(None, line.split(" ")):
        key = key.upper()
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            newline.append(command_keycode)
        else:
            print(f"Unknown key: <{key}>")
    return newline

# Function to run a converted script line
def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

# Send a string using the keyboard layout
def sendString(line):
    layout.write(line)

# Parse lines of Duckyscript
def parseLine(line):
    global defaultDelay
    if line.startswith("REM"):
        pass
    elif line.startswith("DELAY"):
        time.sleep(float(line[6:]) / 1000)
    elif line.startswith("STRING"):
        sendString(line[7:])
    elif line.startswith("PRINT"):
        print("[SCRIPT]: " + line[6:])
    elif line.startswith("IMPORT"):
        runScript(line[7:])
    elif line.startswith("DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif line.startswith("DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    elif line.startswith("LED"):
        led.value = not led.value
    elif line.startswith("WAIT_FOR_BUTTON_PRESS"):
        while not button1.fell:
            button1.update()
    else:
        runScriptLine(convertLine(line))

# Initialize the keyboard
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

# Initialize button and payload pins
button1_pin = DigitalInOut(board.GP22)
button1_pin.pull = Pull.UP
button1 = Debouncer(button1_pin)

payload1Pin = digitalio.DigitalInOut(board.GP4)
payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
payload2Pin = digitalio.DigitalInOut(board.GP5)
payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
payload3Pin = digitalio.DigitalInOut(board.GP10)
payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
payload4Pin = digitalio.DigitalInOut(board.GP11)
payload4Pin.switch_to_input(pull=digitalio.Pull.UP)

# Function to select a payload
def selectPayload():
    if not payload1Pin.value:
        return "payload.dd"
    elif not payload2Pin.value:
        return "payload2.dd"
    elif not payload3Pin.value:
        return "payload3.dd"
    elif not payload4Pin.value:
        return "payload4.dd"
    return "payload.dd"

# IR sensor
ir_sensor = digitalio.DigitalInOut(board.GP17)
ir_sensor.switch_to_input(pull=digitalio.Pull.UP)

# Light sensor
light_sensor = analogio.AnalogIn(board.GP26)

# Function to get light level
def get_light_level():
    return light_sensor.value / 65535

# Function to play a tone using a buzzer
buzzer = pwmio.PWMOut(board.GP15, duty_cycle=0, frequency=440, variable_frequency=True)
def play_tone(frequency, duration):
    buzzer.frequency = frequency
    buzzer.duty_cycle = 65535 // 2  # 50% duty cycle
    time.sleep(duration)
    buzzer.duty_cycle = 0  # Stop the tone

# Function to run a Duckyscript
def runScript(file):
    global defaultDelay
    try:
        with open(file, "r", encoding='utf-8') as f:
            play_tone(1000, 0.5)  # Start alert
            previousLine = ""
            for line in f:
                line = line.rstrip()
                if line.startswith("REPEAT"):
                    for _ in range(int(line[7:])):
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay) / 1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay) / 1000)
            play_tone(1500, 0.5)  # Finished alert
    except OSError as e:
        logging.error(f"Unable to open file: {file}")
        play_tone(500, 1.0)  # Error alert

# Async tasks
async def blink_led(led):
    while True:
        for i in range(100):
            if i < 50:
                led.duty_cycle = int(i * 2 * 65535 / 100)
            await asyncio.sleep(0.01)

async def monitor_buttons():
    button1Down = False
    while True:
        button1.update()
        if button1.fell:
            button1Down = True
        if button1.rose and button1Down:
            payload = selectPayload()
            runScript(payload)
        await asyncio.sleep(0)

async def monitor_ir_sensor():
    while True:
        if not ir_sensor.value:
            runScript(selectPayload())
        await asyncio.sleep(0.1)

async def monitor_light_sensor():
    while True:
        light_level = get_light_level()
        if light_level < 0.2:
            runScript("dark_payload.dd")
        elif light_level > 0.8:
            runScript("bright_payload.dd")
        await asyncio.sleep(0.5)

# Main loop
async def main():
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
    await asyncio.gather(
        blink_led(led),
        monitor_buttons(),
        monitor_ir_sensor(),
        monitor_light_sensor()
    )

# Start async event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program interrupted by user.")
