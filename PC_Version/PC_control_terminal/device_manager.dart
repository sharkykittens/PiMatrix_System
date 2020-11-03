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
  bool sync_ready = false;

  Device(InternetAddress address) {
    this.ip = address;
  }

  void createTCP() async {
    this.tcpConnection = await RawSynchronousSocket.connectSync(this.ip, 8000);
    print("TCP connected!");
    var tcpdata = utf8.decode(tcpConnection.readSync(32));
    this.status = tcpdata[0].toString();
    print(tcpdata); //testing
  }

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

///Represents the controller class to manage all devices
class DeviceManager {
  var deviceList = new List();
  int numDevices = 0;
  bool managerBusy = false;
  bool alreadyexistflag = false;

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

//Function to discover and accept connection from devices
  void discoverDevices() async {
    var udpSocket = await createUDP();
    print(udpSocket); //testing
    udpSocket.broadcastEnabled = true;
    udpSocket = EasyUDPSocket(udpSocket);

    udpSocket.send(utf8.encode('live long and prosper'),
        InternetAddress('192.168.1.255'), 8001);

//Handles all incoming datagram packets until a certain interval where no new datagrams are detected
    while (true) {
      this.alreadyexistflag = false;
      Datagram dg = await udpSocket.receive(timeout: 1000);
      if (dg == null) {
        print("Timeout! No new incoming datagrams");
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
            device.showDevice();
            print("Device added to list!");
          }

          continue;
        }
      }
    }

    print("finished scanning...");

    //for (var pimatrix in this.deviceList) {
    //  await pimatrix.createTCP();
    // pimatrix.showDevice(); //testing
    //}

    this.numDevices = deviceList.length;
    if (this.numDevices > 0) {
      print("there are ${this.numDevices} devices! <- indicator");
    } else {
      print("no devices discovered!");
    }
  }

  void tabulateDevices() {
    print(this.deviceList);
    var num = 1;
    if (this.numDevices > 0) {
      print("\n#\tHostname\tIP\t\tStatus");
      print("-\t--------\t--\t\t------");
      for (var pimatrix in this.deviceList) {
        var status = pimatrix.getStatus();
        switch (status) {
          case 'I':
            {
              status = 'Idle';
            }
            print((num).toString() +
                ".\t" +
                pimatrix.hostname +
                "\t" +
                pimatrix.ip.address.toString() +
                "\t" +
                pimatrix.status);
            num = num + 1;
            break;
          case 'L':
            {
              status = 'Recording';
            }
            print((num).toString() +
                ".\t" +
                pimatrix.hostname +
                "\t" +
                pimatrix.ip.address.toString() +
                "\t" +
                pimatrix.status);
            num = num + 1;
            break;
          default:
            {}
            print((num).toString() +
                ".\t" +
                pimatrix.hostname +
                "\t" +
                pimatrix.ip.address.toString() +
                "\t" +
                pimatrix.status);
            num = num + 1;
            break;
        }
      }
    } else {
      print('No devices found!');
    }
  }

  void syncDevices() async {
    var num_times = 1000;

    Future get_time() async {
      var now = new DateTime.now();
      var timesinceepoch = now.millisecondsSinceEpoch;
      return (timesinceepoch * 0.001).toDouble();
    }

    Future recv(pimatrix, udpSocket) async {
      try {
        Datagram dg = await udpSocket.receive(timeout: 1000);
        print(dg);
        var msg = utf8.decode(dg.data);
        print("received msg:");
        print(msg);
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

    Future send(pimatrix, data, udpSocket) async {
      try {
        print("sending data " + data.toString());
        udpSocket.send(utf8.encode(data), pimatrix.ip, 2468);
        var t = await get_time();
        return t;
      } catch (e) {
        print(e);
        print(pimatrix.hostname.toString() +
            " timed out or encountered error sending sync packets!");
      }
      return 0;
    }

    Future sync_packet(pimatrix, udpSocket) async {
      print("sync packet");
      var t1 = await send(pimatrix, "sync_packet", udpSocket);
      print("master send time is " + (t1).toString());
      var array = await recv(pimatrix, udpSocket);
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

    Future delay_packet(pimatrix, udpSocket) async {
      print("delay packet");
      var unused = send(pimatrix, "delay_packet", udpSocket);
      var array = await recv(pimatrix, udpSocket);
      print(array);
      double t4 = (array[0]);
      double t3 = double.parse(array[1]);
      return t4 - t3;
    }

    void sync_clock(pimatrix, udpSocket) async {
      print("syncing");
      var x = await send(pimatrix, "sync", udpSocket);
      var array = await recv(pimatrix, udpSocket);
      print(array);
      var t = array[0];
      var resp = array[1];

      x = await send(pimatrix, num_times.toString(), udpSocket);
      array = await recv(pimatrix, udpSocket);
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
          var ms_diff = await sync_packet(pimatrix, udpSocket);
          print(ms_diff);
          var sm_diff = await delay_packet(pimatrix, udpSocket);
          print(sm_diff);
          var offset = (ms_diff - sm_diff) / 2;
          var delay = (ms_diff + sm_diff) / 2;
          pimatrix.offsets.add(offset);
          pimatrix.delays.add(delay);
          await send(pimatrix, "next", udpSocket);
          i = i + 1;
        }
        print("done!");

        var final_offset =
            (pimatrix.offsets.reduce((value, element) => value + element)) /
                (pimatrix.offsets.length);
        pimatrix.final_offset = final_offset; //in seconds
        print(pimatrix.final_offset);
        final_offset = final_offset * 1000000000; //in nanoseconds

        var x = await send(pimatrix, "final", udpSocket);
        final_offset = final_offset.toString();
        var z = await send(pimatrix, final_offset, udpSocket); //nanoseconds
      }
    }

    //code execution here
    print("starting syncing...");
    //creates the udpsocket to be used for sending sync messages
    var udpSocket = await createUDP();
    print(udpSocket); //testing
    udpSocket = EasyUDPSocket(udpSocket);

    for (var pimatrix in this.deviceList) {
      await sync_clock(pimatrix, udpSocket);
    }
  }

  void sendCommand(String command) {
    String signal = "";
    switch (command) {
      case "shutdown":
        {
          signal = "T";
        }
        break;
      case "rec2sd":
        {
          signal = "L";
        }
        break;
      case "rec2net":
        {
          signal = "N";
        }
        break;
      case "stop":
        {
          signal = "I";
        }
        break;
      case "sync":
        {
          signal = "S";
        }
        break;
      case "sync_recording":
        {
          signal = "L";
        }
        break;
      case "liveVAD":
        {
          signal = "V";
        }
        break;
      case "VADSyncFlag":
        {
          signal = "F"; //for signalling devices to record when VAD detected
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
    double sample_delay =
        0; //to account for the delay in each iteration of sending
    for (var pimatrix in this.deviceList) {
      try {
        if (command == "sync_recording") {
          double offset_time = 5 - pimatrix.final_offset - sample_delay;
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

      sample_delay =
          sample_delay + 0.001875; //experiment to account for sample delay
    }
  }

  void vad_UDP() async {
    var udpSocket = await createVADUDP();
    print(udpSocket); //testing
    udpSocket.broadcastEnabled = true;
    udpSocket = EasyUDPSocket(udpSocket);
    print("VAD port listening on port 8641");
    while (true) {
      Datagram dg = await udpSocket.receive();
      if (dg == null) {
        print("error!");
        break;
      }
      if (dg != null) {
        var data = utf8.decode(dg.data);
        if (data == 'activate_VAD') {
          print("activate VAD!!!");
          for (var pimatrix in this.deviceList) {
            double offset_time = 1 - pimatrix.final_offset;
            pimatrix.tcpConnection
                .writeFromSync(utf8.encode('F|' + offset_time.toString()));
          }
        }
      }
    }
  }

  void disconnectDevice() {} //in progress

  void disconnectAll() {
    for (var pimatrix in this.deviceList) {
      if (pimatrix.tcpConnection != null) {
        pimatrix.tcpConnection.closeSync();
      }
    }
    this.deviceList = [];
    this.numDevices = 0;
  }

  // function to clear all current streams of data in the tcp connection
  // changes all to non blocking and raising an error, then setting it back to blocking
  void cleanTCPBuffer() {
    for (var pimatrix in this.deviceList) {
      print(pimatrix);
    }
  }
}
