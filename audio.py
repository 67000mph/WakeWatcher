
from timeit import Timer
from pydub import AudioSegment
from pydub.playback import _play_with_pyaudio
import time
import threading

# def play_audio_loop(file_path, duration):
#     try:
#         # Load the audio file
#         audio = AudioSegment.from_wav(file_path)
#         # Play the audio repeatedly for the specified duration
#         start_time = time.time()
#         while time.time() - start_time < duration:
#             _play_with_pyaudio(audio)
#     except Exception as e:
#         print(f"Error occurred during playback: {e}")

class AudioPlayerThread(threading.Thread):
    def __init__(self, file_path, duration):
        super().__init__()
        self.file_path = file_path
        self.duration = duration
        self.stop_event = threading.Event()

    def run(self):
        try:
            audio = AudioSegment.from_wav(self.file_path)
            start_time = time.time()
            while not self.stop_event.is_set() and time.time() - start_time < self.duration:
                _play_with_pyaudio(audio)
        except Exception as e:
            print(f"Error occurred during playback: {e}")

    def stop(self):
        self.stop_event.set()