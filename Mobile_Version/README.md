# PiMatrix System with Mobile Application

## Running the System

1. Ensure that the PiMatrix device is configured to automatically connect to the mobile device's hotspot
2. Start the PiMatrix device and speak the chosen wakeword
3. Wait until the PiMatrix device flashes golden, this means that it is ready for discover
4. Start the mobile application and select Discover Devices.

## PiMatrix

### Configuration:

#### Wakeword

The mobile version of the system is programmed to activate via a wakeword. The script can be found in PiMatrix/wakeword/Snowboy/wakeword.py

This script shutsdown all of the PiMatrix's major functionalities such as HDMI and wifi until it detects the chosen wakeword.

The wakeword can be configured via the Snowboy webservice, it then generates a personal model file (.pmdl) that is unique to each speaker's voice.

The unique wakeword generator can be found here : https://snowboy.kitt.ai/

_WARNING: The unique file generator will be shutdown at the end of 2020, you should generate your model before then_

This script is automatically run by the PiMatrix system upon bootup.

1. Navigate to specified folder
   > cd ~/.config/lxsession/LXDE-pi
2. Edit autorun script
   > sudo nano autostart
3. Include a line to start your program, for example if running a python file:
   > @python your/directory/myfile.py
   > Note that if running a script file:
   > @./superscript
   > _Note that this would run the script in an infinite loop_
4. Restart Raspberry Pi

_WARNING: Please test and ensure that the wakeword works before configuring the script to start on bootup as it may lock you out of the RaspberryPi_

#### Google Drive Upload

Everytime the system is rebooted, it has to manually authenticate with Google Drive in order to be able to upload files.

Firstly, a '<credentials.json>' file should be generated. Follow the steps listed here on how to generate your unique credentials json file.

https://pythonhosted.org/PyDrive/quickstart.html

Next, to automate this process, a '<mycreds.txt>' file has to be generated. This file will use the '<GoogleAuth.LoadCredentialsFile()>' method to automatically authenticate.

The stackoverflow answer here explains this method in more detail: https://stackoverflow.com/a/24542604

### Dependencies:

#### Python Packages:

- PyDrive
- NumPy
- SciPy
- Matrix_lite
- webrtcVAD
- Pause

#### Debian Packages:

## Mobile Device

### Configuration:

This version of the mobile application has been tested in Xcode and iOS devices only. It has yet to be tested on Android devices.

### Dependencies:

- Flutter SDK

dependencies are listed in pubspec.yaml

> flutter pub get
> to resolve dependencies
