
![[Pi_Display.png]]

To use a 3.5 inch TFT touch display with a Raspberry Pi 3, you'll need to install a compatible operating system and configure the display. Here’s a step-by-step guide:

![[Display_Setup.png]]
### Supported Operating Systems
1. **Raspberry Pi OS (formerly Raspbian)**: The most common and officially supported OS.
2. **Kali Linux**: If you're into penetration testing.
3. **RetroPie**: For retro gaming.
4. **Ubuntu MATE**: For a desktop experience.
5. **Windows 10 IoT Core**: For IoT applications.

### Setting Up the 3.5 Inch TFT Touch Display

1. **Prepare Your MicroSD Card**:
   - Download the desired OS image.
	   - [Raspbian](https://www.raspberrypi.com/software/) 
	   - Ubuntu
	   - Kali Linux
   - [Raspberry Pi Imager](https://www.raspberrypi.com/software/) is the quick and easy way to install Raspberry Pi OS and other operating systems to a microSD card, ready to use with your Raspberry Pi. (Use a tool like Rufus Balena Etcher to flash the image onto the microSD card.)

2. **Connect the Display**:
   - Connect the 3.5 inch TFT touch display to the GPIO pins of the Raspberry Pi. Make sure it's securely attached.

	

1. **Boot Your Raspberry Pi**:
   - Insert the microSD card into the Raspberry Pi.
   - Connect the power supply and boot it up.

2. **Install the Necessary Drivers**:
   - Most 3.5 inch TFT displays come with a CD or a link to download drivers. If not, you can usually find drivers on the manufacturer's website or GitHub.

3. **Driver Installation**:
   - Open the terminal and update your system:
     ```bash
     sudo apt update
     sudo apt upgrade
     ```
   - Download the driver package. For example, if using a commonly available driver from GitHub:
     ```bash
     git clone https://github.com/goodtft/LCD-show.git
     ```
   - Navigate to the downloaded directory:
     ```bash
     cd LCD-show
     ```
   - Install the driver. The specific command might vary depending on the display model. For instance, for a 3.5 inch TFT display:
     ```bash
     sudo ./LCD35-show
     ```

6. **Reboot Your Raspberry Pi**:
   - After the installation completes, reboot the Raspberry Pi:
     ```bash
     sudo reboot
     ```

7. **Calibration (if needed)**:
   - If the touch is not accurate, you might need to calibrate the screen. This can often be done using the `xinput_calibrator` tool.
     ```bash
     sudo apt install xinput-calibrator
     xinput_calibrator
     ```

### Troubleshooting
- **Display Not Working**: Ensure the display is correctly connected and try re-seating it.
- **Touch Not Working**: Make sure the touch driver is installed correctly.
- **Calibration Issues**: Re-run the calibration tool.

By following these steps, you should be able to set up and use your 3.5 inch TFT touch display with your Raspberry Pi 3 successfully.

-----

There are several different manufacturers and types of 3.5 inch TFT touch displays for the Raspberry Pi, and they often require specific drivers. Here are a few alternatives to the `goodtft` drivers you can try:

### Alternative Drivers

1. **WaveShare Drivers**:
   WaveShare is a well-known manufacturer of Raspberry Pi displays. Their drivers can be found on their official GitHub repository.

   ```bash
   git clone https://github.com/waveshare/LCD-show.git
   cd LCD-show
   sudo ./LCD35-show
   ```

2. **Elecrow Drivers**:
   Elecrow also provides drivers for their displays. Instructions and drivers are typically provided on their product pages.

   ```bash
   git clone https://github.com/Elecrow-keen/Elecrow-LCD35.git
   cd Elecrow-LCD35
   sudo ./Elecrow-LCD35-show
   ```

3. **KeDei Drivers**:
   KeDei offers a variety of displays with their own drivers available on their website or GitHub.

   ```bash
   git clone https://github.com/KeDei/lcd35-driver.git
   cd lcd35-driver
   sudo ./install.sh
   ```

4. **Notro's FBTFT Drivers**:
   Notro's FBTFT drivers support a wide range of TFT displays. These drivers are integrated into the Raspberry Pi Linux kernel, so you might not need to clone a repository. Instead, you can directly configure the device tree overlay.

   ```bash
   sudo modprobe fbtft_device name=<driver_name>
   ```

   Replace `<driver_name>` with the appropriate driver name for your display. You can find the list of supported drivers [here](https://github.com/notro/fbtft).

### Generic Steps for Installing Other Drivers

1. **Download and Install the Driver**:
   - Clone the repository with the driver.
   - Navigate to the downloaded directory.
   - Run the installation script or follow the instructions provided in the repository's README file.

2. **Configure the Display**:
   - After installing the driver, the display might need additional configuration. This often involves editing configuration files such as `/boot/config.txt` or `/etc/modules`.

3. **Reboot**:
   - After making the necessary changes, reboot your Raspberry Pi to apply the new settings.

   ```bash
   sudo reboot
   ```

### Example for WaveShare 3.5 Inch TFT Display

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/waveshare/LCD-show.git
   ```

2. **Navigate to the Directory**:
   ```bash
   cd LCD-show
   ```

3. **Run the Installation Script**:
   ```bash
   sudo ./LCD35-show
   ```

4. **Reboot**:
   ```bash
   sudo reboot
   ```

### Troubleshooting

- **Check Connections**: Ensure all connections are secure.
- **Compatibility**: Verify that the driver is compatible with your specific display model.
- **Logs**: Check logs for errors using `dmesg` or by examining `/var/log/syslog`.

By using the correct driver for your display, you should be able to achieve a functional setup on your Raspberry Pi 3 with the 3.5 inch TFT touch display.

-----

Here is a comprehensive list of alternative drivers for 3.5 inch TFT touch displays for the Raspberry Pi. These drivers come from different manufacturers and community contributions.

### 1. **GoodTFT Drivers**

**GitHub Repository**:
```bash
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
sudo ./LCD35-show
```

### 2. **Waveshare Drivers**

**GitHub Repository**:
```bash
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show
sudo ./LCD35-show
```

### 3. **Elecrow Drivers**

**GitHub Repository**:
```bash
git clone https://github.com/Elecrow-keen/Elecrow-LCD35.git
cd Elecrow-LCD35
sudo ./Elecrow-LCD35-show
```

### 4. **KeDei Drivers**

**GitHub Repository**:
```bash
git clone https://github.com/KeDei/lcd35-driver.git
cd lcd35-driver
sudo ./install.sh
```

### 5. **Notro's FBTFT Drivers**

These drivers are part of the Raspberry Pi Linux kernel, so you don't need to clone a repository. Instead, you configure the device tree overlay directly.

**Commands**:
```bash
sudo modprobe fbtft_device name=<driver_name>
```
Replace `<driver_name>` with the appropriate driver name for your display. You can find the list of supported drivers [here](https://github.com/notro/fbtft).

### 6. **WaveShare SpotPear Drivers**

**GitHub Repository**:
```bash
git clone https://github.com/swkim01/waveshare-dtoverlays.git
cd waveshare-dtoverlays
sudo ./install.sh
```

### 7. **LCD-Show Drivers by juj/fbcp-ili9341**

For displays using the ILI9341 controller.

**GitHub Repository**:
```bash
git clone https://github.com/juj/fbcp-ili9341.git
cd fbcp-ili9341
mkdir build
cd build
cmake ..
make -j
sudo ./fbcp-ili9341
```

### 8. **LCD-Show Drivers by tianyoujian**

**GitHub Repository**:
```bash
git clone https://github.com/tianyoujian/LCD-show.git
cd LCD-show
sudo ./LCD35-show
```

### 9. **XPT2046 Touch Controller Drivers**

For displays using the XPT2046 touch controller.

**GitHub Repository**:
```bash
git clone https://github.com/juj/fbcp-ili9341.git
cd fbcp-ili9341
mkdir build
cd build
cmake -DADAFRUIT_ILI9341=ON -DXPT2046=ON ..
make -j
sudo ./fbcp-ili9341
```

### Installation Steps for All Drivers

1. **Prepare Your MicroSD Card**:
   - Download the desired OS image.
   - Use a tool like Balena Etcher to flash the image onto the microSD card.

2. **Connect the Display**:
   - Connect the 3.5 inch TFT touch display to the GPIO pins of the Raspberry Pi. Make sure it's securely attached.

3. **Boot Your Raspberry Pi**:
   - Insert the microSD card into the Raspberry Pi.
   - Connect the power supply and boot it up.

4. **Download and Install the Driver**:
   - Clone the repository with the driver.
   - Navigate to the downloaded directory.
   - Run the installation script or follow the instructions provided in the repository's README file.

5. **Reboot Your Raspberry Pi**:
   - After making the necessary changes, reboot your Raspberry Pi to apply the new settings.
   ```bash
   sudo reboot
   ```

### Troubleshooting

- **Check Connections**: Ensure all connections are secure.
- **Compatibility**: Verify that the driver is compatible with your specific display model.
- **Logs**: Check logs for errors using `dmesg` or by examining `/var/log/syslog`.

By using the correct driver for your display, you should be able to achieve a functional setup on your Raspberry Pi 3 with the 3.5 inch TFT touch display.

-----

### References

-  http://www.lcdwiki.com/3.5inch_RPi_Display
- https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(A)