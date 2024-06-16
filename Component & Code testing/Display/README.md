---

---
-----
# Setting Up the 3.5-Inch TFT Raspberry Pi Display

## Introduction
The 3.5-inch TFT display is a touch screen designed for the Raspberry Pi. It offers a compact and convenient way to interact with your Raspberry Pi projects.

![[Pi_Display.png]]
## Components and Specifications
### Display Specifications:
- **Screen Size**: 3.5 inches
- **Resolution**: 480x320 pixels
- **Touch Panel**: Resistive touch
- **Interface**: SPI

### Electrical Specifications:
- **Input Voltage**: 5V (from Raspberry Pi)
- **Current**: Approximately 100mA (without backlight)

### Pin Configuration:
| Pin Number             | Function | Description                            |
| ---------------------- | -------- | -------------------------------------- |
| 1 (3.3V)               | 3.3V     | Power supply for the display logic     |
| 2 (5V)                 | 5V       | Power supply for the display backlight |
| 3 (GPIO2)              | SDA      | I2C data                               |
| 5 (GPIO3)              | SCL      | I2C clock                              |
| 19 (GPIO10)            | MOSI     | SPI data input                         |
| 21 (GPIO9)             | MISO     | SPI data output                        |
| 23 (GPIO11)            | SCLK     | SPI clock                              |
| 24 (GPIO8)             | CE0      | SPI chip select                        |
| 22 (GPIO25)            | D/C      | Data/Command control                   |
| 18 (GPIO24)            | RST      | Reset                                  |
| 16 (GPIO23)            | TP_CS    | Touch panel chip select                |
| 12 (GPIO18)            | TP_IRQ   | Touch panel interrupt                  |
| 6, 9, 14, 20, 25 (GND) | GND      | Ground                                 |

![[Display_Setup.png]]
## Setting Up the Display

### Step 1: Hardware Connection
1. **Turn off your Raspberry Pi** to prevent any damage during the connection.
2. **Connect the Display to the Raspberry Pi**:
    - Align the display's GPIO pins with the Raspberry Pi's GPIO header.
    - Carefully press the display onto the Raspberry Pi, ensuring all pins are correctly aligned.

### Step 2: Install the Driver
To use the display with your Raspberry Pi, you need to install the appropriate drivers. Here’s how:

1. **Update the System**:
    ```bash
    sudo apt-get update
    sudo apt-get upgrade
    ```

2. **Download the Driver**:
    ```bash
    git clone https://github.com/waveshare/LCD-show.git
    cd LCD-show/
    ```

3. **Install the Driver**:
    - For the 3.5-inch display:
        ```bash
    chmod +x LCD35-show
	./LCD35-show
        ```

4. **Reboot the Raspberry Pi**:
    ```bash
    sudo reboot
    ```

### Step 3: Configure the Touchscreen (Optional)
If you want to calibrate the touchscreen:

1. **Install the calibration tool**:
    ```bash
    sudo apt-get install -y xinput-calibrator
    ```

2. **Run the calibration tool**:
    ```bash
    DISPLAY=:0.0 xinput_calibrator
    ```

3. Follow the on-screen instructions to calibrate the touch screen.

### Step 4: Verify the Setup
After rebooting, the display should show the Raspberry Pi desktop environment. You can test the touchscreen functionality and ensure everything works correctly.

## Troubleshooting
- **Display not turning on**: Ensure all GPIO connections are secure and the Raspberry Pi is powered on.
- **Touchscreen not responding**: Recalibrate the touchscreen using the calibration tool.
- **Screen flickering**: Check the power supply and ensure the Raspberry Pi is receiving enough power.

## Additional Resources
- [Waveshare Wiki for 3.5-inch RPi LCD](https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(A))
- [LCD Wiki for 3.5-inch RPi Display](http://www.lcdwiki.com/3.5inch_RPi_Display)

## Conclusion
Setting up the 3.5-inch TFT display on your Raspberry Pi is straightforward with the right steps and drivers. This guide provides detailed instructions to ensure a smooth installation and configuration process. Enjoy your new touch screen interface for your Raspberry Pi projects!

---
