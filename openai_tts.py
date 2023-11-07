import io
import openai
import os
from pydub import AudioSegment
from pydub.playback import play

openai.api_key = "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"

def stream_and_play(text):
    response = openai.audio.speech.create(
        model="tts-1-hd",
        voice='shimmer',
        input=text
    )

    byte_stream = io.BytesIO(response.content)

    audio = AudioSegment.from_file(byte_stream, format='mp3')

    play(audio)


if __name__ == "__main__":
    text = input("Enter text: ")
    stream_and_play(text)
