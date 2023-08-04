from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the window at the top left corner with 0 width and height
        self.setGeometry(0, 0, 0, 1169)

        # Create the animation for the geometry
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)  # Duration in milliseconds
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(0, 0, 650, 0))
        self.animation.setEasingCurve(QEasingCurve.Type.Linear)

        self.animation.start()
        self.setStyleSheet("QMainWindow {background-image: url(screenshot.png); background-position: top left; background-repeat: no-repeat;}")
        self.setWindowTitle("Abbey")
        label = QLabel("Hi there, ", self)
        label.setGeometry(100, 100, 200, 30)
        label.setStyleSheet("QLabel { background-color: black; color: white; }") 

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
