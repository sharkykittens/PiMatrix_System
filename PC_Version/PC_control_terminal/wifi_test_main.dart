import 'device_manager.dart';
import 'dart:io';
import 'dart:isolate';

void main() async {
  var deviceManager = new DeviceManager();
  print(deviceManager);

  while (true) {
    print("Please key in command");
    print("1 : Discover Devices");
    print("2 : List all Connected Devices");
    print("3 : Record Audio");
    print("4 : Stop Recording");
    print("5 : Disconnect all Devices");
    print("6 : Shut Down");
    print("7 : Synchronize Devices");
    print("8 : Record with VAD enabled");
    print("9 : Record with DOA enabled"); //in progress
    print("10 : Record using Wakeword"); //in progress
    print("11 : Synced Recording Mode (please synchronize devices first)");
    print("12 : Upload Files");

    int input = int.parse(stdin.readLineSync());

    switch (input) {
      case 1:
        {
          print("Searching for devices...");
          sleep(const Duration(seconds: 1));
          await deviceManager.discoverDevices();
        }
        break;
      case 2:
        {
          print("Listing all currently connected devices");
          sleep(const Duration(seconds: 1));
          deviceManager.tabulateDevices();
        }
        break;
      case 3:
        {
          print("Recording...");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("rec2sd");
        }
        break;
      case 4:
        {
          print("Stopping Recording...");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("stop");
        }
        break;
      case 5:
        {
          print("Disconnecting all devices...");
          sleep(const Duration(seconds: 1));
          deviceManager.disconnectAll();
        }
        break;
      case 6:
        {
          print("Shutting Down...");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("shutdown");
          deviceManager.disconnectAll();
          exit(1);
        }
        break;
      case 7:
        {
          print("Attempting to Sync PiMatrix Devices..");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("sync");
          await deviceManager.syncDevices();
        }
        break;
      case 8:
        {
          print("Live Voice Activity Detection Mode..");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("liveVAD");
          await deviceManager.vad_UDP();
        }
        break;
      case 9:
        {
          print("Live Direction of Arrival Mode..");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("liveDOA");
        }
        break;
      case 10:
        {
          print("Live Wakeword Recording Mode..");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("wakeword");
        }
        break;
      case 11:
        {
          print("Synced Recording Mode...");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("sync_recording");
        }
        break;
      case 12:
        {
          print("Attempting to upload files...");
          sleep(const Duration(seconds: 1));
          deviceManager.sendCommand("upload");
        }
        break;
      default:
        {
          print("Invalid input please try again!");
        }
        break;
    }
  }
}
