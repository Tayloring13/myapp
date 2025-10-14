import wave

filename = "test.wav"
duration_seconds = 1
sample_rate = 16000  # Hz
num_samples = duration_seconds * sample_rate

# Create silent audio
with wave.open(filename, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(sample_rate)
    wf.writeframes(b'\x00\x00' * num_samples)

print(f"Created {filename}")