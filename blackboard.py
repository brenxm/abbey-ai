import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFrame, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.frame = QFrame(self)
        layout = QVBoxLayout()

        paragraph = "This is a sample paragraph. You can replace this with any text you want."

        self.label = QLabel(paragraph)
        self.label.setStyleSheet("background-color: black; padding: 10%; color: white;") # Black background, 10% padding
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) # Align text to top-left
        layout.addWidget(self.label)

        self.button = QPushButton("Minimize", self)
        self.button.clicked.connect(self.minimize)
        layout.addWidget(self.button)

        self.frame.setLayout(layout)
        self.setCentralWidget(self.frame)

        # Get the screen size
        screen_size = self.screen().size()

        # Set the window width and height
        self.width = 700
        self.height = screen_size.height()

        # Set the window position to the right of the screen
        self.setGeometry(screen_size.width() - self.width, 0, self.width, self.height)

        # Animate the window from right to left
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500) # 0.5 second
        self.animation.setStartValue(QRect(screen_size.width(), 0, self.width, self.height))
        self.animation.setEndValue(QRect(screen_size.width() - self.width, 0, self.width, self.height))
        self.animation.start()

    def minimize(self):
        screen_size = self.screen().size()
        
        # Reverse animation for minimizing
        self.animation.setStartValue(QRect(screen_size.width() - self.width, 0, self.width, self.height))
        self.animation.setEndValue(QRect(screen_size.width(), 0, self.width, self.height))
        self.animation.finished.connect(self.hide) # Hide the window when the animation is done
        self.animation.start()
        
    def stream(self, text):
        self.label = QLabel(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
