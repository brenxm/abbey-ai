import sounddevice as sd
from time import sleep
import threading
from scipy.io import wavfile
import io
import subprocess

class AudioPlayer():
    def __init__(self, tts_queue):
        self.is_playing = False
        self.queue = []
        self.is_pause = False
        self.tts_queue = tts_queue

    def stop(self):
        self.is_playing = False
        
    def load_to_queue(self, audio):
        self.queue.append(audio)
        
    def pause(self):
        self.is_pause = True
        
    def resume(self):
        self.is_pause = False
        
    def _start_player(self):
        self.is_playing = True
        audio_bytes = self.queue.pop(0)
        
        if type(audio_bytes).__name__ == "bytes":
            rate, data = wavfile.read(io.BytesIO(audio_bytes))
            # Play the WAV file using sounddevice
       
            sleep(0.15)
            sd.play(data, rate)
            sd.wait()  # Wait for the playback to finish
            
        else:
            subprocess.Popen(['python', 'gui/blackboard.py'], stdout=subprocess.PIPE)
            
        
        if len(self.queue) > 0:
            self._start_player()
        
        else:
            self.is_playing = False

                
    def listen(self):
        # Thread is already allocated for this audio player if playing, ensure to use a thread only when it's not playing
        if not self.is_playing:
            player_thread = threading.Thread(target=self._start_player)
            player_thread.start()