# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)

import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
from board import *
import pwmio
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard

# Keyboard Layout imports (US layout)
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# Duckyscript command dictionary
duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12,
}
def convertLine(line):
    newline = []
    for key in filter(None, line.split(" ")):
        key = key.upper()
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            newline.append(command_keycode)
        elif hasattr(Keycode, key):
            newline.append(getattr(Keycode, key))
        else:
            print(f"Unknown key: <{key}>")
    return newline

def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
    global defaultDelay
    if(line[0:3] == "REM"):
        pass
    elif(line[0:5] == "DELAY"):
        time.sleep(float(line[6:])/1000)
    elif(line[0:6] == "STRING"):
        sendString(line[7:])
    elif(line[0:5] == "PRINT"):
        print("[SCRIPT]: " + line[6:])
    elif(line[0:6] == "IMPORT"):
        runScript(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    elif(line[0:3] == "LED"):
        if(led.value == True):
            led.value = False
        else:
            led.value = True
    elif(line[0:21] == "WAIT_FOR_BUTTON_PRESS"):
        button_pressed = False
        while not button_pressed:
            button1.update()
            if(button1.fell):
                print("Button 1 pushed")
                button_pressed = True
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

# Initialize button
button1_pin = DigitalInOut(GP22)
button1_pin.pull = Pull.UP
button1 = Debouncer(button1_pin)

# Initialize payload selection switch
payload1Pin = digitalio.DigitalInOut(GP4)
payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
payload2Pin = digitalio.DigitalInOut(GP5)
payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
payload3Pin = digitalio.DigitalInOut(GP10)
payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
payload4Pin = digitalio.DigitalInOut(GP11)
payload4Pin.switch_to_input(pull=digitalio.Pull.UP)

def getProgrammingStatus():
    progStatusPin = digitalio.DigitalInOut(GP0)
    progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
    progStatus = not progStatusPin.value
    return(progStatus)

def runScript(file):
    global defaultDelay
    try:
        with open(file, "r", encoding='utf-8') as f:
            previousLine = ""
            for line in f:
                line = line.rstrip()
                if line.startswith("REPEAT"):
                    for _ in range(int(line[7:])):
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
    except OSError as e:
        print("Unable to open file", file)

def selectPayload():
    global payload1Pin, payload2Pin, payload3Pin, payload4Pin
    if not payload1Pin.value:
        return "payload.dd"
    elif not payload2Pin.value:
        return "payload2.dd"
    elif not payload3Pin.value:
        return "payload3.dd"
    elif not payload4Pin.value:
        return "payload4.dd"
    else:
        return "payload.dd"

async def blink_led(led):
    if board.board_id == 'raspberry_pi_pico':
        await blink_pico_led(led)
    elif board.board_id == 'raspberry_pi_pico_w':
        await blink_pico_w_led(led)

async def blink_pico_led(led):
    led_state = False
    while True:
        for i in range(100):
            if i < 50:
                led.duty_cycle = int(i * 2 * 65535 / 100)
            await asyncio.sleep(0.01)
        led_state = not led_state

async def blink_pico_w_led(led):
    led_state = False
    while True:
        led.value = int(led_state)
        led_state = not led_state
        await asyncio.sleep(0.5)

async def monitor_buttons(button1):
    button1Down = False
    while True:
        button1.update()
        if button1.fell:
            button1Down = True
        if button1.rose and button1Down:
            payload = selectPayload()
            print("Running", payload)
            runScript(payload)
        button1Down = False
        await asyncio.sleep(0)
def runScript(file):
    global defaultDelay
    try:
        with open(file, "r", encoding='utf-8') as f:
            previousLine = ""
            display_on_oled(f"Running: {file}")  # Display file name
            for line in f:
                line = line.rstrip()
                if line.startswith("REPEAT"):
                    for _ in range(int(line[7:])):
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
    except OSError as e:
        print(f"Unable to open file: {file}")
        display_on_oled("Error: File not found")  # Display error on OLED

# Define a payload schedule
payload_schedule = [
    {"file": "payload.dd", "delay": 2},  # Delay of 2 seconds
    {"file": "payload2.dd", "delay": 5},  # Delay of 5 seconds
    {"file": "payload3.dd", "delay": 3},  # Delay of 3 seconds
]

# Function to run scheduled payloads
async def run_scheduled_payloads():
    for payload in payload_schedule:
        display_on_oled(f"Running: {payload['file']}")
        runScript(payload['file'])
        await asyncio.sleep(payload['delay'])  # Delay between payloads
import logging

# Initialize logging
logging.basicConfig(filename="/log.txt", level=logging.ERROR)

def runScript(file):
    global defaultDelay
    try:
        with open(file, "r", encoding='utf-8') as f:
            previousLine = ""
            display_on_oled(f"Running: {file}")
            for line in f:
                line = line.rstrip()
                if line.startswith("REPEAT"):
                    for _ in range(int(line[7:])):
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
    except OSError as e:
        error_msg = f"Error: Unable to open {file}"
        print(error_msg)
        display_on_oled(error_msg)
        logging.error(error_msg)
# Initialize the IR sensor pin
ir_sensor = digitalio.DigitalInOut(GP17)
ir_sensor.switch_to_input(pull=digitalio.Pull.UP)

async def monitor_ir_sensor():
    while True:
        if not ir_sensor.value:  # When motion is detected
            display_on_oled("Motion Detected")
            payload = selectPayload()
            runScript(payload)
        await asyncio.sleep(0.1)
import pwmio

buzzer = pwmio.PWMOut(board.GP15, duty_cycle=0, frequency=440, variable_frequency=True)

# Function to play a tone
def play_tone(frequency, duration):
    buzzer.frequency = frequency
    buzzer.duty_cycle = 65535 // 2  # 50% duty cycle
    time.sleep(duration)
    buzzer.duty_cycle = 0  # Stop the tone
def runScript(file):
    global defaultDelay
    try:
        with open(file, "r", encoding='utf-8') as f:
            play_tone(1000, 0.5)  # Start alert
            previousLine = ""
            display_on_oled(f"Running: {file}")
            for line in f:
                line = line.rstrip()
                if line.startswith("REPEAT"):
                    for _ in range(int(line[7:])):
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            play_tone(1500, 0.5)  # Finished alert
    except OSError as e:
        print(f"Unable to open file: {file}")
        display_on_oled("Error: File not found")
        logging.error(f"Error: Unable to open {file}")
        play_tone(500, 1.0)  # Error alert
import analogio

light_sensor = analogio.AnalogIn(board.GP26)

# Function to get light level
def get_light_level():
    return light_sensor.value / 65535  # Normalize to 0-1
async def monitor_light_sensor():
    while True:
        light_level = get_light_level()
        if light_level < 0.2:
            payload = "dark_payload.dd"
            runScript(payload)
        elif light_level > 0.8:
            payload = "bright_payload.dd"
            runScript(payload)
        await asyncio.sleep(0.5)


async def main():
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
    await asyncio.gather(
        blink_led(led),              # LED blinking functionality
        monitor_buttons(button1),    # Button press monitoring
        monitor_ir_sensor(),         # IR sensor monitoring
        monitor_light_sensor(),      # Light sensor monitoring
        serve_web(),                 # Web interface for remote control
        run_scheduled_payloads()     # Run scheduled payloads
    )

# Start the async event loop
asyncio.run(main())
