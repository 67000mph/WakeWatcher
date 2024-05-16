import sys
from PyQt5.QtWidgets import QApplication
import gui
import audio

if __name__ == "__main__":
    file_path = "arrow-whoosh.wav"
    duration = 10  # Playback duration in seconds
    
    audio_player = audio.AudioPlayerThread(file_path, duration)
    
    app = QApplication(sys.argv)
    window = gui.MainWindow(audio_player)

    sys.exit(app.exec_())     