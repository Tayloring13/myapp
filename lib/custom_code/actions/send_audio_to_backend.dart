import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:audioplayers/audioplayers.dart';

bool useLocalBackend = true; // true = local testing, false = Railway

Future<void> sendAudioToBackend(String filePath) async {
  final uri = Uri.parse(
      useLocalBackend
          ? 'http://127.0.0.1:8000/chat'
          : 'https://japanaut-backend.up.railway.app/chat'
  ); // Replace with your exact Railway endpoint

  var request = http.MultipartRequest('POST', uri);

  // Add the recorded audio file
  request.files.add(await http.MultipartFile.fromPath('audio', filePath));

  // Send the request
  var response = await request.send();

  if (response.statusCode == 200) {
    final responseBody = await response.stream.bytesToString();
    final data = json.decode(responseBody);
    final audioUrl = data['audio_url'];
    final player = AudioPlayer();
    await player.play(UrlSource(audioUrl));
  } else {
    print('Error: ${response.statusCode}');
  }
}