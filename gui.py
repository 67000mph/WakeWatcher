from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QWidget, QTextEdit, QComboBox, QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QSpinBox
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2
from PyQt5.QtCore import QTimer, QDateTime, Qt, QTime
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
import motion_detection
import audio

class MainWindow(QWidget):
    def __init__(self, audio_player_thread):
        super().__init__()
        self.audio_player_thread = audio_player_thread

        self.setWindowTitle("Wake Watcher")

        self.label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

        self.clock_label = QLabel(self)
        self.layout.addWidget(self.clock_label)

        self.create_input_box()
        self.layout.addWidget(self.input_box)

        self.textbox = QTextEdit(self)
        self.textbox.setReadOnly(True)
        self.layout.addWidget(self.textbox)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)
        self.cap = cv2.VideoCapture(0)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

        self.status_jumping_jack = 0
        self.reset_Time_jumping_jack = 0
        self.status_push_up = 0
        self.reset_Time_push_up = 0

        self.show()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame, jumping_jack_detected, push_up_detected = self.detect_and_draw_pose(frame)
            frame_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            image = QPixmap.fromImage(frame_image)
            self.label.setPixmap(image)
            if jumping_jack_detected:
                self.textbox.append("Jumping Jack detected!")
            if push_up_detected:
                self.textbox.append("Push-up detected!")

    def detect_and_draw_pose(self, frame):
        results = self.pose.process(frame)
        jumping_jack_detected = False
        push_up_detected = False
        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark
            cTime = QTime.currentTime().second()
            jumping_jack_detected, self.status_jumping_jack, self.reset_Time_jumping_jack = motion_detection.check_jumping_jack(
                landmarks, self.status_jumping_jack, cTime, self.reset_Time_jumping_jack
            )
            push_up_detected, self.status_push_up, self.reset_Time_push_up = motion_detection.check_push_up(
                landmarks, self.status_push_up, cTime, self.reset_Time_push_up
            )
        return frame, jumping_jack_detected, push_up_detected

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.clock_label.setText("Current Time: " + current_time)
        self.clock_label.setFont(QFont("Arial", 32))
        if self.time_input.time_edit.text() == current_time:
            self.textbox.append("Der Wecker klingelt!")
            self.textbox.append(f"Mache {self.exc_reps.value()} {self.exc_select.currentText()}")
            self.audio_player_thread.start()
            # Problem when called again -> Threads can only be started once!

    def append_text(self, text):
        self.textbox.append(text)

    def create_input_box(self):
        self.input_box = QGroupBox("Einstellungen")
        layout = QFormLayout()
        self.time_input = TimeInputWidget()
        layout.addRow(QLabel("Weckzeit:"), self.time_input)
        self.exc_select = QComboBox()
        self.exc_select.addItem("Liegestütz")
        self.exc_select.addItem("Hampelmann")
        layout.addRow(QLabel("Übung:"), self.exc_select)
        self.exc_reps = QSpinBox()
        layout.addRow(QLabel("Wiederholungen:"), self.exc_reps)
        self.input_box.setLayout(layout)

class TimeInputWidget(QWidget):
  def __init__(self, parent=None):
    super(TimeInputWidget, self).__init__(parent)
    self.layout = QHBoxLayout()

    self.hours_box = QSpinBox()
    self.hours_box.setRange(0, 23)
    self.hours_box.setFixedWidth(40)
    self.hours_box.valueChanged.connect(self.update_text)

    self.minutes_box = QSpinBox()
    self.minutes_box.setRange(0, 59)
    self.minutes_box.setFixedWidth(40)
    self.minutes_box.valueChanged.connect(self.update_text)

    self.seconds_box = QSpinBox()
    self.seconds_box.setRange(0, 59)
    self.seconds_box.setFixedWidth(40)
    self.seconds_box.valueChanged.connect(self.update_text)

    self.separator_label1 = QLabel(":")
    self.separator_label1.setAlignment(Qt.AlignCenter)
    self.separator_label2 = QLabel(":")
    self.separator_label2.setAlignment(Qt.AlignCenter)

    self.time_edit = QLineEdit()
    self.time_edit.setReadOnly(True)
    self.time_edit.setAlignment(Qt.AlignCenter)
    self.time_edit.setFixedWidth(70)

    self.layout.addWidget(self.hours_box)
    self.layout.addWidget(self.separator_label1)
    self.layout.addWidget(self.minutes_box)
    self.layout.addWidget(self.separator_label2)
    self.layout.addWidget(self.seconds_box)
    self.layout.addWidget(self.time_edit)

    self.update_text()

    self.setLayout(self.layout)

  def update_text(self):
    hours = self.hours_box.value()
    minutes = self.minutes_box.value()
    seconds = self.seconds_box.value()
    
    time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    self.time_edit.setText(time_string)

  def get_time(self):
    return self.time_edit.text()
