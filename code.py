
import board
import digitalio
import storage

# Initialize GP15 pin to check the storage status
noStoragePin = digitalio.DigitalInOut(board.GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = noStoragePin.value

# Determine the USB visibility state based on the board type
if board.board_id == 'raspberry_pi_pico':
    # On Pi Pico, USB is visible if GP15 is not connected
    noStorage = not noStorageStatus
elif board.board_id == 'raspberry_pi_pico_w':
    # On Pi Pico W, USB is hidden if GP15 is not connected
    noStorage = noStorageStatus

# Enable or disable the USB drive based on the noStorage flag
if noStorage:
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    print("USB drive enabled")
