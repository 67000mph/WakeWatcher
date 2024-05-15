from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QWidget, QTextEdit, QComboBox, QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QSpinBox
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2
from PyQt5.QtCore import QTimer, QDateTime, Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

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

        self.show()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QPixmap.fromImage(QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888))
            self.label.setPixmap(image)

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.clock_label.setText("Current Time: " + current_time)
        self.clock_label.setFont(QFont("Arial", 32))
        # self.append_text("The current time is " + current_time)

    def append_text(self, text):
        self.textbox.append(text)

    def create_input_box(self):
        self.input_box = QGroupBox("Einstellungen")
        layout = QFormLayout()
        time_input = TimeInputWidget()
        layout.addRow(QLabel("Weckzeit:"), time_input)
        exc_select = QComboBox()
        exc_select.addItem("Liegestütz")
        exc_select.addItem("Hampelmann")
        layout.addRow(QLabel("Übung:"), exc_select)
        layout.addRow(QLabel("Wiederholungen:"), QSpinBox())
        self.input_box.setLayout(layout)

class TimeInputWidget(QWidget):
  def __init__(self, parent=None):
    super(TimeInputWidget, self).__init__(parent)
    self.layout = QHBoxLayout()

    # Hours input
    self.hours_box = QSpinBox()
    self.hours_box.setRange(0, 23)
    self.hours_box.setFixedWidth(40)
    # Connect valueChanged signal to update_text slot
    self.hours_box.valueChanged.connect(self.update_text)

    # Minutes input
    self.minutes_box = QSpinBox()
    self.minutes_box.setRange(0, 59)
    self.minutes_box.setFixedWidth(40)
    # Connect valueChanged signal to update_text slot
    self.minutes_box.valueChanged.connect(self.update_text)

    # Seconds input
    self.seconds_box = QSpinBox()
    self.seconds_box.setRange(0, 59)
    self.seconds_box.setFixedWidth(40)
    # Connect valueChanged signal to update_text slot
    self.seconds_box.valueChanged.connect(self.update_text)

    # Separator label 1
    self.separator_label1 = QLabel(":")
    self.separator_label1.setAlignment(Qt.AlignCenter)

    # Separator label 2
    self.separator_label2 = QLabel(":")
    self.separator_label2.setAlignment(Qt.AlignCenter)

    # Time display
    self.time_edit = QLineEdit()
    self.time_edit.setReadOnly(True)
    self.time_edit.setAlignment(Qt.AlignCenter)
    self.time_edit.setFixedWidth(70)

    # Add widgets to layout
    self.layout.addWidget(self.hours_box)
    self.layout.addWidget(self.separator_label1)
    self.layout.addWidget(self.minutes_box)
    self.layout.addWidget(self.separator_label2)
    self.layout.addWidget(self.seconds_box)
    self.layout.addWidget(self.time_edit)

    # Initial update
    self.update_text()

    self.setLayout(self.layout)

  def update_text(self):
    # Get the current values from the spin boxes
    hours = self.hours_box.value()
    minutes = self.minutes_box.value()
    seconds = self.seconds_box.value()
    
    # Format the time as hh:mm:ss
    time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Update the time display
    self.time_edit.setText(time_string)

  def get_time(self):
    return self.time_edit.text()
