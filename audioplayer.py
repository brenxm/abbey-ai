import sounddevice as sd
import wavio
from time import sleep
import threading
from scipy.io import wavfile
import os
import io


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
        while(True):
            while self.is_pause:
                print("on pause")
                sleep(0.5) 
                
            if len(self.queue) > 0:
                audio_bytes = self.queue.pop(0)
                rate, data = wavfile.read(io.BytesIO(audio_bytes))
                # Play the WAV file using sounddevice
                sd.play(data, rate)
                sd.wait()  # Wait for the playback to finish
                print('played audio')
                    
                
            else:
                if not self.is_playing and len(self.queue) <= 0 and len(self.tts_queue) <= 0:
                    print('ended listening')
                    break
                
            sleep(0.05)
                
    def listen(self):
        self.is_playing = True
        player_thread = threading.Thread(target=self._start_player)
        player_thread.start()