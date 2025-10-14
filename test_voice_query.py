import requests

url = "http://127.0.0.1:8000/voice-query"
file_path = r"C:\Users\taylo\myapp-clean\Voice_test.wav"

with open(file_path, "rb") as f:
    files = {"audio": (file_path, f, "audio/wav")}
    resp = requests.post(url, files=files)

if resp.status_code == 200:
    with open("reply.wav", "wb") as out:
        out.write(resp.content)
    print("Success! reply.wav saved.")
else:
    print("Error:", resp.status_code, resp.text)