
from timeit import Timer
from pydub import AudioSegment
from pydub.playback import play
import time

def play_audio_loop(file_path):
    # Lade die Audio-Datei
    audio = AudioSegment.from_wav(file_path)
    play(audio)
    
if __name__ == "__main__":
    file_path = "C:\\Users\\marce\\arrow-whoosh.wav"
    zeit = 0
    print("Start Alarm Clock")
    while(zeit<=10):
        play_audio_loop(file_path)
        time.sleep(1)
        zeit+=1

    print("End Alarm Clock")
  
 