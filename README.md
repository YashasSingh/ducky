
# Project Name

This project utilizes a Raspberry Pi Pico to interact with various peripherals like buttons, sensors, and a keyboard. It runs Duckyscript commands and provides feedback through LED indicators, a buzzer, and a light sensor.

## Features

- **Keyboard Control**: Send keyboard commands using Duckyscript.
- **Button Monitoring**: Detect button presses to trigger scripts.
- **IR Sensor**: Execute scripts when motion is detected.
- **Light Sensor**: Execute scripts based on ambient light levels.
- **LED Feedback**: Blink LED to indicate status.
- **Buzzer Alerts**: Play tones to signal events (e.g., script start and end).
- **Payload Scheduling**: Run scheduled payloads with delays.

## Components

- Raspberry Pi Pico
- Push Buttons
- IR Sensor
- Light Sensor
- LED
- Buzzer

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Install Libraries**

   Install the necessary libraries for the project. This can be done using CircuitPython's bundle or manually if needed.

3. **Connect Components**

   Connect the components to the Raspberry Pi Pico according to the following pin assignments:

   - Button 1: GP22
   - Payload Switches: GP4, GP5, GP10, GP11
   - IR Sensor: GP17
   - Light Sensor: GP26
   - LED: GP25
   - Buzzer: GP15

4. **Upload Code**

   Upload the code to your Raspberry Pi Pico.

## Usage

1. **Running Scripts**

   - Scripts can be executed by pressing the button connected to GP22.
   - The active payload is selected based on the position of the payload switches.

2. **Script Formats**

   Scripts should be in the following format:

   - `REM`: Comment line.
   - `DELAY <milliseconds>`: Wait for the specified amount of time.
   - `STRING <text>`: Send a string of text.
   - `PRINT <message>`: Print a message to the console.
   - `IMPORT <filename>`: Import and execute another script.
   - `DEFAULT_DELAY <milliseconds>`: Set default delay for script execution.
   - `LED`: Toggle the LED.
   - `WAIT_FOR_BUTTON_PRESS`: Wait for button press before continuing.
   - `REPEAT <count>`: Repeat the previous line a specified number of times.

3. **Monitoring Sensors**

   - The IR sensor will trigger the current payload when motion is detected.
   - The light sensor will execute `dark_payload.dd` or `bright_payload.dd` based on the light level.

## Logging

Errors and important events are logged in `log.txt`. Make sure to check this file if you encounter issues.

## License

This project is licensed under the [GPLv2.0 License](LICENSE).

