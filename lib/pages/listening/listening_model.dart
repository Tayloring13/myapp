import '/flutter_flow/flutter_flow_util.dart';
import 'listening_widget.dart' show ListeningWidget;
import 'package:flutter/material.dart';
import 'package:record/record.dart';

class ListeningModel extends FlutterFlowModel<ListeningWidget> {
  ///  State fields for stateful widgets in this page.

  AudioRecorder? audioRecorder;
  String? recordedAudioFile;
  FFUploadedFile recordedFileBytes =
      FFUploadedFile(bytes: Uint8List.fromList([]));

  @override
  void initState(BuildContext context) {}

  @override
  void dispose() {}
}
