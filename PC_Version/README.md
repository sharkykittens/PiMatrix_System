# PiMatrix System to be used only with PiMatrix System and PC

## Running The System

1. Ensure that the PiMatrix Device and PC are connected to the same network
2. Start the script '<python3 pimatrix_firmware.py>' on the PiMatrix device
3. Start the script '<dart pc_control_terminal.dart> on the PC

## PiMatrix

### Dependencies:

#### Python Packages:

- PyDrive
- NumPy
- SciPy
- Matrix_lite
- webrtcVAD
- Pause

#### Google Drive Upload

Everytime the system is rebooted, it has to manually authenticate with Google Drive in order to be able to upload files.

Firstly, a '<credentials.json>' file should be generated. Follow the steps listed here on how to generate your unique credentials json file.

https://pythonhosted.org/PyDrive/quickstart.html

Next, to automate this process, a '<mycreds.txt>' file has to be generated. This file will use the '<GoogleAuth.LoadCredentialsFile()>' method to automatically authenticate.

The stackoverflow answer here explains this method in more detail: https://stackoverflow.com/a/24542604

## PC Control Terminal

### Configuration

### Depedencies

- dart SDK
  get dependencies by running

> pub get
