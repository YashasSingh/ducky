
import board
import digitalio
import storage

# Initialize GP15 to determine USB visibility state
noStoragePin = digitalio.DigitalInOut(board.GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
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

# Control USB drive visibility based on noStorage flag
if noStorage:
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    print("USB drive enabled")
