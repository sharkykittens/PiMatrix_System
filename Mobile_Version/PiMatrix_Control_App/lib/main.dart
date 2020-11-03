import 'package:flutter/material.dart';
import 'package:bloc/bloc.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'text_observer.dart';
import 'logic.dart';

void main() {
  Bloc.observer = TextObserver();
  runApp(MyApp());
}

class MyApp extends MaterialApp {
  const MyApp({Key key}) : super(key: key, home: const AppPage());
}

class AppPage extends StatelessWidget {
  const AppPage({Key key}) : super(key: key);
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => DeviceManager(),
      child: AppView(),
    );
  }
}

class AppView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'PiMatrix Remote',
        home: Scaffold(
          appBar: AppBar(
            title: Text('PiMatrix Remote'),
          ),
          body: BodyContent(),
          bottomSheet: BottomBar(),
        ));
  }
}

class BodyContent extends StatelessWidget {
  BodyContent({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        children: <Widget>[
          Expanded(
              child: Row(
            children: [
              Container(
                  color: Colors.orange,
                  width: 50,
                  height: 300,
                  child: Column(children: [
                    Container(
                      color: Colors.red,
                      width: 50,
                      height: 30,
                      child: Text('#',
                          style: TextStyle(fontSize: 20),
                          textAlign: TextAlign.center),
                    ),
                    Container(
                        color: Colors.blue[100],
                        width: 50,
                        height: 255.7,
                        child: ListView(children: <Widget>[
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['#'][0].toString()));
                          }),
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['#'][1].toString()));
                          }),
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['#'][2].toString()));
                          })
                        ]))
                  ])),
              Container(
                  color: Colors.blue,
                  width: 170,
                  height: 300,
                  child: Column(children: [
                    Container(
                      color: Colors.red,
                      width: 170,
                      height: 30,
                      child: Text('Device',
                          style: TextStyle(fontSize: 20),
                          textAlign: TextAlign.center),
                    ),
                    Container(
                        color: Colors.blue[100],
                        width: 170,
                        height: 255.7,
                        child: ListView(children: <Widget>[
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['device'][0].toString()));
                          }),
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['device'][1].toString()));
                          }),
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['device'][2].toString()));
                          })
                        ]))
                  ])),
              Container(
                  width: 150,
                  height: 300,
                  color: Colors.purple,
                  child: Column(children: [
                    Container(
                      color: Colors.red,
                      width: 150,
                      height: 30,
                      child: Text('Status',
                          style: TextStyle(fontSize: 20),
                          textAlign: TextAlign.center),
                    ),
                    Container(
                        color: Colors.blue[100],
                        width: 150,
                        height: 255.7,
                        child: ListView(children: <Widget>[
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['status'][0].toString()));
                          }),
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['status'][1].toString()));
                          }),
                          BlocBuilder<DeviceManager, Map>(
                              builder: (context, state) {
                            return ListTile(
                                title: Text(state['status'][2].toString()));
                          })
                        ]))
                  ])),
            ],
          )),
          const Divider(color: Colors.blue),
          Expanded(
              child: Column(
            children: <Widget>[
              Container(
                  height: 63.75,
                  width: 375,
                  color: Colors.blue[50],
                  child: Row(children: <Widget>[
                    ButtonBar(
                      children: <Widget>[
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () => context
                                    .bloc<DeviceManager>()
                                    .discoverDevices(),
                                child: Text("Discover Devices"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () =>
                                    context.bloc<DeviceManager>().syncDevicesTCP(),
                                child: Text("Sync Devices"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () {
                                  context
                                      .bloc<DeviceManager>()
                                      .sendCommand('shutdown');
                                  context.bloc<DeviceManager>().disconnectAll();
                                },
                                child: Text("Shut Down"))),
                      ],
                    )
                  ])),
              Container(
                  height: 63.75,
                  width: 375,
                  color: Colors.blue[100],
                  child: Row(children: <Widget>[
                    ButtonBar(
                      children: <Widget>[
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () {
                                  context
                                      .bloc<DeviceManager>()
                                      .sendCommand('rec2sd');
                                },
                                child: Text("Record"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () {
                                  context.bloc<DeviceManager>().vad_UDP();
                                  context
                                      .bloc<DeviceManager>()
                                      .sendCommand('liveVAD');
                                },
                                child: Text("Record with VAD"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                key: const Key(
                                    'some_key_here_to_identify_button'),
                                onPressed: () => context
                                    .bloc<DeviceManager>()
                                    .sendCommand('stop'),
                                child: Text("Stop Record"))),
                      ],
                    )
                  ])),
              Container(
                  height: 63.75,
                  width: 375,
                  color: Colors.blue[200],
                  child: Row(children: <Widget>[
                    ButtonBar(
                      children: <Widget>[
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () => context
                                    .bloc<DeviceManager>()
                                    .sendCommand('upload'),
                                child: Text("Upload Files"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () => context.bloc<DeviceManager>().sendCommand('sync_recording'),
                                child: Text("Synced Recording"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () {},
                                child: Text("Button Button"))),
                      ],
                    )
                  ])),
              Container(
                  height: 63.75,
                  width: 375,
                  color: Colors.blue[300],
                  child: Row(children: <Widget>[
                    ButtonBar(
                      children: <Widget>[
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () {},
                                child: Text("Button Button"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () {},
                                child: Text("Button Button"))),
                        SizedBox(
                            width: 114,
                            height: 47,
                            child: RaisedButton(
                                onPressed: () =>
                                    context.bloc<DeviceManager>().cubitTest(),
                                child: Text("Cubit Test"))),
                      ],
                    )
                  ])),
            ],
          ))
        ],
      ),
    );
  }
}

class BottomBar extends StatelessWidget {
  BottomBar({Key key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BottomAppBar(
        child: Container(
            width: 1000,
            height: 40,
            color: Colors.blueGrey,
            child: BlocBuilder<DeviceManager, Map>(
              builder: (context, state) {
                return Text(state['debug_text'].toString(),
                    style: TextStyle(fontSize: 20),
                    textAlign: TextAlign.center);
              },
            )));
  }
}
