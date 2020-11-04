import 'dart:async';

import 'package:easy_udp_socket/easy_udp_socket.dart';
import 'dart:io';
import 'dart:convert' show utf8;

///Represents the individual device that will connect to the device manager.
class Device {
  String hostname = "";
  String status = "";
  List offsets = [];
  List delays = [];
  double final_offset =
      0; //to be updated after syncing devices, if not the default is 0
  InternetAddress ip;
  RawSynchronousSocket tcpConnection;
  RawSynchronousSocket tcpSync;
  bool sync_ready = false;

  Device(InternetAddress address) {
    this.ip = address;
  }

  Future createTCP() async {
    this.tcpConnection = await RawSynchronousSocket.connectSync(this.ip, 8000);
    print("TCP connected!");
    var tcpdata = utf8.decode(tcpConnection.readSync(32));
    this.status = tcpdata[0].toString();
    print(tcpdata); //testing
  }

  Future createTCPSync() async {
    this.tcpSync = await RawSynchronousSocket.connectSync(this.ip, 8640);
    print("TCP Sync connected!");
  } //this tcp connection for sync

  String getStatus() {
    return this.status;
  }

  String getHostname() {
    return this.hostname;
  }

  void setHostname(String hostname) {
    this.hostname = hostname;
  }

  void showDevice() {
    print("Showing Device...");
    print(this.hostname);
    print(this.status);
    print(this.offsets);
    print(this.delays);
    print(this.ip);
    print(this.tcpConnection);
    print(this.final_offset);
  }

  ///End of Device Class
}

/// Represents the controller class to manage all devices.
/// Emit state is stored as a Map for easier UI updating.

class DeviceManager {
  var deviceList = new List();
  int numDevices = 0;
  bool managerBusy = false;
  bool alreadyexistflag = false;
  bool interrupt_vad_loop = false;

//use future to ensure program halts until UDP Socket is created and ready to use
  Future createUDP() async {
    var udpSocket = RawDatagramSocket.bind(InternetAddress.anyIPv4, 0);
    return udpSocket;
  }

  Future createSyncUDP() async {
    var udpSocket = RawDatagramSocket.bind(InternetAddress.anyIPv4, 2468);

    return udpSocket;
  }

  Future createVADUDP() async {
    var udpSocket = RawDatagramSocket.bind(InternetAddress.anyIPv4, 8641);
    return udpSocket;
  }

  /// Function to discover and accept connection from devices.
  /// Creates a UDP handshake and then constructs the Device object in memory

  void discoverDevices() async {
    var udpSocket = await createUDP();
    print(udpSocket); //testing
    udpSocket.broadcastEnabled = true;
    udpSocket = EasyUDPSocket(udpSocket);
    List<InternetAddress> hotspot_addresses = [
      InternetAddress('172.20.10.2'),
      InternetAddress('172.20.10.3'),
      InternetAddress('172.20.10.4'),
      InternetAddress('172.20.10.5'),
      InternetAddress('172.20.10.6'),
      InternetAddress('172.20.10.7'),
      InternetAddress('172.20.10.8'),
      InternetAddress('172.20.10.9'),
      InternetAddress('172.20.10.10'),
      InternetAddress('172.20.10.11'),
      InternetAddress('172.20.10.12'),
      InternetAddress('172.20.10.13'),
      InternetAddress('172.20.10.14'),
    ];

    udpSocket.send(utf8.encode('live long and prosper'),
        InternetAddress('192.168.1.255'), 8001);

// code to send handshake to all possible ip addresses on iOS wifi hotspot

    for (var address in hotspot_addresses) {
      udpSocket.send(utf8.encode('live long and prosper'), address, 8001);
    }

//Handles all incoming datagram packets until a certain interval where no new datagrams are detected
    while (true) {
      this.alreadyexistflag = false;
      Datagram dg = await udpSocket.receive(timeout: 1000);
      if (dg == null) {
        print("Timeout! no new incoming datagrams");

        break;
      }
      if (dg != null) {
        var data = utf8.decode(dg.data);
        print(data);
        var splitdata = data.split("|");
        if (splitdata[0] == 'peace and long life') {
          print("discovered device " + dg.address.toString());
          //check if this device already exists in the list, if it does do not add it again

          for (var pimatrix in this.deviceList) {
            print(pimatrix); //testing
            if (splitdata[1].toString() == pimatrix.getHostname()) {
              this.alreadyexistflag = true;
              print("Device already exists! Not adding again.");
              break;
            } else {
              continue;
            }
          }
          if (this.alreadyexistflag == false) {
            var device = new Device(dg.address);
            device.setHostname(splitdata[1]);
            this.deviceList.add(device);
            await device.createTCP();
            await device.createTCPSync(); //create the tcp connection for sync
            device.showDevice();
            print("Device added to list!");
          }

          continue;
        }
      }
    }

    print("Finished Scanning...");

    this.numDevices = deviceList.length;
    if (this.numDevices > 0) {
      print("there are ${this.numDevices} devices!");

      tabulateDevices();
    } else {
      print("no devices discovered!");
    }
  }

  void tabulateDevices() {
    print(this.deviceList);

    if (this.numDevices > 0) {
      //print("\n#\tHostname\tIP\t\tStatus");
      //print("-\t--------\t--\t\t------");
      for (var pimatrix in this.deviceList) {
        var status = pimatrix.getStatus();
      }
    } else {
      print('No devices found!');
    }
  }

  /// The below function and all subfunctions are used for PTP synchronization via TCP.
  /// Stores the final offset value in each Device object after synchronization completed.

  void syncDevicesTCP() async {
    var num_times = 200;

    Future get_time() async {
      var now = new DateTime.now();
      var timesinceepoch = now.millisecondsSinceEpoch;
      return (timesinceepoch * 0.001).toDouble();
    }

    Future recv(pimatrix) async {
      try {
        var dg = pimatrix.tcpSync.readSync(4096);

        //print(dg);
        var msg = utf8.decode(dg);

        //print("received msg:");
        //print(msg);
        var t = await get_time();
        var array = [t, msg];
        print(array);
        return array;
      } catch (e) {
        print(e);
        print(pimatrix.hostname.toString() +
            " timed out or encountered error reading sync packets!");
      }
      return [];
    }

    Future send(pimatrix, data) async {
      try {
        //print("sending data " + data.toString());
        pimatrix.tcpSync.writeFromSync(utf8.encode(data));

        var t = await get_time();
        return t;
      } catch (e) {
        print(e);
        print(pimatrix.hostname.toString() +
            " timed out or encountered error sending sync packets!");
      }
      return 0;
    }

    Future sync_packet(pimatrix) async {
      print("sync packet");
      var t1 = await send(pimatrix, "sync_packet");
      print("master send time is " + (t1).toString());
      var array = await recv(pimatrix);
      print("array is " + array.toString());
      var index0 = array[0];
      var index1 = array[1];
      print(index0);
      print(index1);
      double t = index0;
      double t2 = double.parse(index1);
      print("sync packet is calculated " +
          (t2).toString() +
          "-" +
          (t1).toString());
      return (t2 - t1);
    }

    Future delay_packet(pimatrix) async {
      print("delay packet");
      var unused = send(pimatrix, "delay_packet");
      var array = await recv(pimatrix);
      print(array);
      double t4 = (array[0]);
      double t3 = double.parse(array[1]);
      return t4 - t3;
    }

    void sync_clock(pimatrix) async {
      print("syncing");
      var x = await send(pimatrix, "sync");
      var array = await recv(pimatrix);
      print(array);
      var t = array[0];
      var resp = array[1];

      x = await send(pimatrix, num_times.toString());
      array = await recv(pimatrix);
      print(array);
      t = array[0];
      resp = array[1];

      print(resp);
      var i = 0;
      if (resp == "ready") {
        print("ready to begin sync process");
        await sleep(const Duration(seconds: 1));
        while (i < num_times) {
          print("loop number " + i.toString());
          var ms_diff = await sync_packet(pimatrix);
          print(ms_diff);
          var sm_diff = await delay_packet(pimatrix);
          print(sm_diff);
          var offset = (ms_diff - sm_diff) / 2;
          var delay = (ms_diff + sm_diff) / 2;
          pimatrix.offsets.add(offset);
          pimatrix.delays.add(delay);
          await send(pimatrix, "next");
          i = i + 1;
        }
        print("done!");

        var final_offset =
            (pimatrix.offsets.reduce((value, element) => value + element)) /
                (pimatrix.offsets.length);
        pimatrix.final_offset = final_offset; //in seconds

        print(pimatrix.final_offset); //in seconds
        final_offset = final_offset * 1000000000; //in nanoseconds

        var x = await send(pimatrix, "final");
        final_offset = final_offset.toString();
        var z = await send(pimatrix, final_offset); //send in nanoseconds
      }
    }

    //code execution here
    print("starting syncing...");

    this.managerBusy = true;
    for (var pimatrix in this.deviceList) {
      await sync_clock(pimatrix);
    }
    this.managerBusy = false;
  }

  /// Function that sends command via TCP to all connected Devices.

  void sendCommand(String command) {
    String signal = "";
    print(command);
    switch (command) {
      case "shutdown":
        {
          signal = "T";
        }
        break;
      case "rec2sd":
        {
          if (this.managerBusy == true) {
            print("invalid action! Devices busy!");
            signal = "";
          } else {
            signal = "L";
            this.managerBusy = true;
          }
        }
        break;
      case "rec2net":
        {
          signal = "N";
        }
        break;
      case "stop":
        {
          this.managerBusy = false;
          signal = "I";
          this.interrupt_vad_loop = true;
        }
        break;
      case "sync":
        {
          signal = "S";
        }
        break;
      case "sync_recording":
        {
          if (this.managerBusy == true) {
            print("invalid action! Devices busy!");

            signal = "";
          } else {
            signal = "L";
            this.managerBusy = true;
          }
        }
        break;
      case "liveVAD":
        {
          if (this.managerBusy == true) {
            print("invalid action! Devices busy!");
            signal = "";
          } else {
            signal = "V";
            this.managerBusy = true;
          }
        }
        break;
      case "upload":
        {
          signal = "G";
        }
        break;
      default:
        {
          print("invalid command!");
          signal = "";
        }
        break;
    }

    double sample_delay = 0;
    //variable to account for the delay in each iteration of sending

    double get_time() {
      var now = new DateTime.now();
      var timesinceepoch = now.millisecondsSinceEpoch;
      return (timesinceepoch * 0.001).toDouble();
    }

    double reference_time = get_time();
    this.tabulateDevices();
    for (var pimatrix in this.deviceList) {
      try {
        if (command == "sync_recording") {
          double offset_time = 1 - pimatrix.final_offset;
          print("OFFSET TIME FOR " +
              pimatrix.getHostname() +
              " IS " +
              offset_time.toString());
          pimatrix.tcpConnection
              .writeFromSync(utf8.encode("L|" + offset_time.toString()));
          pimatrix.status = signal;
        } else {
          pimatrix.tcpConnection.writeFromSync(utf8.encode(signal));
          pimatrix.status = signal;
        }
      } catch (e) {
        print(e);
        print(
            pimatrix.hostname.toString() + " timed out or encountered error!");
      }

      //sample_delay = sample_delay + (get_time()-reference_time);
      //print("the current sample delay is "+sample_delay.toString());

    }
  }

  /// Creates a Port to receive messges while doing voice activity detection.
  /// Sends out messages via TCP to all devices to start collecting audio frames.
  /// Can be interrupted with the "stop" command by using the interrupt_vad_loop flag

  void vad_UDP() async {
    var udpSocket = await createVADUDP();
    print(udpSocket); //testing
    udpSocket.broadcastEnabled = true;
    udpSocket = EasyUDPSocket(udpSocket);
    this.interrupt_vad_loop = false;
    print("VAD port listening on port 8641");
    while (this.interrupt_vad_loop == false) {
      Datagram dg = await udpSocket.receive(timeout: 1000);
      if (dg == null) {
        print("");
      }
      if (dg != null) {
        var data = utf8.decode(dg.data);
        if (data == 'activate_VAD') {
          print("activate VAD!");

          for (var pimatrix in this.deviceList) {
            double offsetTime = 1 - pimatrix.final_offset;
            print("VAD offset time is " + offsetTime.toString());
            pimatrix.tcpConnection
                .writeFromSync(utf8.encode('F|' + offsetTime.toString()));
          }
        }
      }
      print("test");
    }
    print("exit VAD");
    await udpSocket.close();
  }

  void disconnectDevice() {} //in progress

  void disconnectAll() {
    for (var pimatrix in this.deviceList) {
      if (pimatrix.tcpConnection != null) {
        pimatrix.tcpConnection.closeSync();
        pimatrix.tcpSync.closeSync();
      }
    }
    this.deviceList = [];
    this.numDevices = 0;
  }

  // function to clear all current streams of data in the tcp connection
  // changes all to non blocking and raising an error, then setting it back to blocking
  void cleanTCPBuffer() {
    for (var pimatrix in this.deviceList) {
      var trash = [];
      pimatrix.tcpConnection.readIntoSync(trash);
    }
  }
}
