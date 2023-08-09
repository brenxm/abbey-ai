from PyQt6.QtWidgets import QApplication, QMainWindow, QFrame, QPushButton, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QWidget, QTextEdit, QScrollArea
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QSize
from PyQt6.QtGui import QIcon, QKeyEvent, QTextDocument
import sys


class TextareaSubmitEvent(QTextEdit):
    def __init__(self, chatbox_layout):
        super().__init__()
        self.chatbox_layout = chatbox_layout

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            text = self.toPlainText()
            available_width = self.chatbox_layout.parentWidget().parentWidget().width() - 20 # Adjust based on padding and margins
            label = ChatBubble(text, available_width)
            self.chatbox_layout.addWidget(label)
            self.clear()
        else:
            super().keyPressEvent(event)


class ChatBubble(QLabel):
    def __init__(self, text, available_width):
        super().__init__()
        self.padding = 10
        self.text_content = text
        self.setWordWrap(True)
        self.setText(text)
        self.setStyleSheet(f"margin: 5px; padding: {self.padding}px; border-radius: 7px; background-color: rgb(40, 40, 40);")
        self.resizeForText(available_width)

    def resizeForText(self, available_width):
        text_document = QTextDocument()
        text_document.setDefaultFont(self.font())
        text_document.setHtml(self.text_content)
        text_document.setTextWidth(available_width - 2 * self.padding)
        new_height = text_document.size().height() + 2 * self.padding
        self.setFixedHeight(int(new_height))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: rgb(50, 50, 50)")
        layout = QVBoxLayout()

        # Response Layout
        response_layout = QVBoxLayout()
        response_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        response_container = QWidget()
        response_container.setLayout(response_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(response_container)
        layout.addWidget(self.scroll_area, stretch=1)

        # Input Layout
        input_layout_bg = QWidget()
        input_layout_bg.setStyleSheet("background-color: rgb(70, 70, 70); border-radius: 7.5px")
        input_layout_bg.setFixedHeight(50)
        textarea = TextareaSubmitEvent(response_layout)
        textarea.setFixedHeight(50)
        send_btn = QPushButton()
        icon = QIcon("gui/send_btn.png")
        send_btn.setIcon(icon)
        send_btn.setIconSize(QSize(25, 25))
        send_btn.setStyleSheet("padding: 15px")

        component_input_layout = QHBoxLayout()
        component_input_layout.addWidget(textarea)
        component_input_layout.addWidget(send_btn)
        input_layout_bg.setLayout(component_input_layout)
        layout.addWidget(input_layout_bg, stretch=0)

        self.frame.setLayout(layout)
        self.setCentralWidget(self.frame)
        self.setupWindowAnimation()

    def setupWindowAnimation(self):
        screen_size = self.screen().size()
        self.width = 600
        self.height = screen_size.height()

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(screen_size.width(), 0, self.width, self.height - 500))
        self.animation.setEndValue(QRect(screen_size.width() - self.width, 0, self.width, self.height - 500))
        self.animation.start()

    def minimize(self):
        screen_size = self.screen().size()

        # Reverse animation for minimizing
        self.animation.setStartValue(QRect(screen_size.width() - self.width, 0, self.width, self.height))
        self.animation.setEndValue(QRect(screen_size.width(), 0, self.width, self.height))
        self.animation.finished.connect(self.hide)
        self.animation.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
