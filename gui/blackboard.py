import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window size and position
        self.setFixedSize(600, 900)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(screen_geometry.width() - self.width(), 0)

        # Create a central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        padding = 20
        layout.setContentsMargins(padding, padding, padding, padding)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set background color for the main layout and title bar
        main_color = "#333333"
        central_widget.setStyleSheet(f"background-color: {main_color};")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(main_color))
        self.setPalette(palette)

        # Read the text file content
        try:
            with open('gui/message_transfer.txt', 'r') as file:
                text = file.read()
        except FileNotFoundError:
            text = "File not found"

        # Create a QLabel element with the text
        label = QLabel(text)
        
        try:
            with open('gui/message_transfer.txt', 'w') as file:
                file.write("")
        except FileNotFoundError:
            text = "File not found"
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        label.setStyleSheet("""
            QLabel {
                background-color: #222222;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        # Add QLabel to the layout
        layout.addWidget(label)

        # Show the window
        self.show()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())

