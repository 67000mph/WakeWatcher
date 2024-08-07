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
    def __init__(self):
        super().__init__()
        self.audio_player_thread = None

        self.setWindowTitle("Wake Watcher")

        self.img_label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.img_label)

        self.clock_label = QLabel(self)
        self.layout.addWidget(self.clock_label)

        self.exc_image_label = QLabel()
        self.layout.addWidget(self.exc_image_label)

        self.create_input_box()
        self.layout.addWidget(self.input_box)

        self.textbox = QTextEdit(self)
        self.textbox.setReadOnly(True)
        font = QFont()
        font.setPointSize(16)
        self.textbox.setFont(font)
        self.layout.addWidget(self.textbox)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.img_label)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.clock_label)
        right_layout.addWidget(self.input_box)
        right_layout.addWidget(self.exc_image_label)
        right_layout.addWidget(self.textbox)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

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
        self.status_squat = 0
        self.reset_Time_squat = 0

        self.exc_count = 0
        self.alarm_active = False

        self.show()

    def closeEvent(self, event):
        self.audio_player_thread.stop()
        super().closeEvent(event)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame, jumping_jack_detected, push_up_detected, squat_detected = self.detect_and_draw_pose(frame)
            frame_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            image = QPixmap.fromImage(frame_image)
            width = image.width() * 1.65
            height = image.height() * 1.65
            scaled_image = image.scaled(int(width), int(height), Qt.KeepAspectRatio)
            self.img_label.setPixmap(scaled_image)
            if jumping_jack_detected:
                if self.exc_select.currentText() == "Hampelmann":
                    self.count_reps()
            if push_up_detected:
                if self.exc_select.currentText() == "Liegestütz":
                    self.count_reps()
            if squat_detected:
                if self.exc_select.currentText() == "Kniebeuge":
                    self.count_reps()

    def count_reps(self):
        if self.alarm_active:
            self.exc_count += 1
            self.textbox.append(f"{self.exc_count}")
            if self.exc_count >= int(self.exc_reps.text()):
                self.alarm_active = False
                self.audio_player_thread.stop()
                self.audio_player_thread = None
                self.textbox.append("Fertig!")

    def detect_and_draw_pose(self, frame):
        results = self.pose.process(frame)
        jumping_jack_detected = False
        push_up_detected = False
        squat_detected = False
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
            squat_detected, self.status_squat, self.reset_Time_squat = motion_detection.check_squat(
                landmarks, self.status_squat, cTime, self.reset_Time_squat
            )
        return frame, jumping_jack_detected, push_up_detected, squat_detected

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.clock_label.setText("Aktuelle Uhrzeit: " + current_time)
        self.clock_label.setFont(QFont("Arial", 40))
        if self.time_input.time_edit.text() == current_time:
            self.textbox.append("Der Wecker klingelt!")
            self.textbox.append(f"Mache {self.exc_reps.value()} {self.exc_select.currentText()}")
            self.audio_player_thread = audio.AudioPlayerThread(audio.ALARM_FILE)
            self.audio_player_thread.start()
            self.alarm_active = True
            self.exc_count = 0

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
        self.exc_select.addItem("Kniebeuge")     
        self.exc_select.currentIndexChanged.connect(self.update_image)
        self.exc_select.setCurrentIndex(self.exc_select.findText("Liegestütz"))
        self.update_image() 

        layout.addRow(QLabel("Übung:"), self.exc_select)
        self.exc_reps = QSpinBox()
        layout.addRow(QLabel("Wiederholungen:"), self.exc_reps)
        self.input_box.setLayout(layout)
        font_size = 20
        self.input_box.setStyleSheet(f"*{{font-size: {font_size}pt;}}")
        self.input_box.setFixedSize(600, 200) 

    def update_image(self):
                selected_exercise = self.exc_select.currentText() 
                if selected_exercise == "Liegestütz":
                    image_path = "Liegestütz.jpg" 
                elif selected_exercise == "Hampelmann":
                    image_path = "Hampelmann.jpg" 
                elif selected_exercise == "Kniebeuge":
                    image_path = "Kniebeuge.jpg" 
                else:
                    image_path = None 

                if image_path:
                    loaded_image = QImage(image_path)
                    if loaded_image.isNull():
                        print(f"Error loading image: {image_path}")
                    else:
                        resized_image = loaded_image.scaled(800, 800, Qt.KeepAspectRatio)
                        if not resized_image.isNull():
                            print("SUCCESS")
                        else:
                            print("IS NULL")
                        self.exc_image_label.setPixmap(QPixmap(resized_image))
                else:
                    self.exc_image_label.clear()

                # if image_path:
                #     self.exc_image_label.setPixmap(QPixmap(image_path))
                # else:
                #     self.exc_image_label.clear() 


class TimeInputWidget(QWidget):
  def __init__(self, parent=None):
    super(TimeInputWidget, self).__init__(parent)
    self.layout = QHBoxLayout()

    self.hours_box = QSpinBox()
    self.hours_box.setRange(0, 23)
    self.hours_box.setFixedWidth(52)
    self.hours_box.setAlignment(Qt.AlignCenter)
    self.hours_box.valueChanged.connect(self.update_text)

    self.minutes_box = QSpinBox()
    self.minutes_box.setRange(0, 59)
    self.minutes_box.setFixedWidth(52)
    self.minutes_box.setAlignment(Qt.AlignCenter)
    self.minutes_box.valueChanged.connect(self.update_text)

    self.seconds_box = QSpinBox()
    self.seconds_box.setRange(0, 59)
    self.seconds_box.setFixedWidth(52)
    self.seconds_box.setAlignment(Qt.AlignCenter)
    self.seconds_box.valueChanged.connect(self.update_text)

    self.separator_label1 = QLabel(":")
    self.separator_label1.setAlignment(Qt.AlignCenter)
    self.separator_label2 = QLabel(":")
    self.separator_label2.setAlignment(Qt.AlignCenter)

    self.time_edit = QLineEdit()
    self.time_edit.setReadOnly(True)
    self.time_edit.setAlignment(Qt.AlignCenter)
    self.time_edit.setFixedWidth(140)

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
