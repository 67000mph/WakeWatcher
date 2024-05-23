from pydub import AudioSegment
from pydub.playback import _play_with_pyaudio
import threading

ALARM_FILE = "arrow-whoosh.wav"

class AudioPlayerThread(threading.Thread):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.stop_event = threading.Event()

    def run(self):
        try:
            audio = AudioSegment.from_wav(self.file_path)
            while not self.stop_event.is_set():
                _play_with_pyaudio(audio)
        except Exception as e:
            print(f"Error occurred during playback: {e}")

    def stop(self):
        self.stop_event.set()