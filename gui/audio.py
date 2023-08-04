from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)

        self.player.setSource(QUrl.fromLocalFile("audio_queue/output02082023083921.wav"))
        self.audioOutput.setVolume(1)  # 50 percent volume

        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(self.player.play)
        layout.addWidget(self.playButton)

        self.pauseButton = QPushButton('Pause')
        self.pauseButton.clicked.connect(self.player.pause)
        layout.addWidget(self.pauseButton)

        self.stopButton = QPushButton('Stop')
        self.stopButton.clicked.connect(self.player.stop)
        layout.addWidget(self.stopButton)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication([])
    window = AudioPlayer()
    window.show()
    app.exec()
