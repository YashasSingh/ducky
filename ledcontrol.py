

import board
import digitalio
import storage

# Setup for GP15 (USB visibility control) and an LED on GP25
noStoragePin = digitalio.DigitalInOut(board.GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)

led = digitalio.DigitalInOut(board.GP25)  # Assuming LED is connected to GP25
led.direction = digitalio.Direction.OUTPUT

noStorageStatus = noStoragePin.value

# Determine USB visibility based on the board type and GP15 state
if board.board_id == 'raspberry_pi_pico':
    # On Pi Pico, GP15 not connected means USB is visible
    noStorage = not noStorageStatus
elif board.board_id == 'raspberry_pi_pico_w':
    # On Pi Pico W, GP15 not connected means USB is hidden
    noStorage = noStorageStatus
else:
    # Handle unexpected board types
    raise RuntimeError(f"Unsupported board: {board.board_id}")

# Control USB drive visibility and LED indicator
if noStorage:
    storage.disable_usb_drive()
    led.value = True  # Turn on LED to indicate the USB drive is hidden
    print("USB drive disabled, LED ON")
else:
    led.value = False  # Turn off LED to indicate the USB drive is enabled
    print("USB drive enabled, LED OFF")
