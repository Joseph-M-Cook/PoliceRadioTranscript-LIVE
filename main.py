import requests
import openai
import vlc
from pydub.playback import play
from pydub import AudioSegment, silence
import time
import io
import threading
import pydub.playback as playback


# Initialize OpenAI API
openai.api_key = ''

def TestStreamSpeakers(stream_id):
    '''
    This function tests the Broadcastify stream endpoint on
    machines speakers through VLC. Purposed for debugging
    and testing obfuscated HTTP requests for exposed endpoints.

    :param int stream_id: The stream we are trying to connect to.
    '''

    # Configure streaming source endpoint URL
    stream = f'https://broadcastify.cdnstream1.com/{stream_id}'

    # Create a VLC instance and media player
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(stream)
    player.set_media(media)

    # Play the stream
    player.play()

    # Keep the script running to continue playing the stream
    input("Press Enter to stop playing...")
    player.stop()

def TranscribeStreamWithWhisper(stream_id, silence_thresh=-50.0, min_silence_len=1000):
    '''
    This function captures a Broadcastify stream in real-time, 
    chunks the audio based on silence, and transcribes each chunk using
    OpenAI's Whisper.

    :param int stream_id: The stream we are trying to connect to.
    '''
    # Configure streaming source endpoint URL
    stream_url = f'https://broadcastify.cdnstream1.com/{stream_id}'

    # Initialize an empty buffer to hold audio data
    audio_buffer = AudioSegment.empty()

    # Start streaming
    stream_data = requests.get(stream_url, stream=True)

    for chunk in stream_data.iter_content(chunk_size=1024):
        if chunk:
            # Append chunk to buffer
            audio_buffer += AudioSegment.from_mp3(io.BytesIO(chunk))

            # Check for silence in the buffer
            silent_chunks = silence.detect_silence(audio_buffer, silence_thresh=silence_thresh, min_silence_len=min_silence_len)

            # If silence is detected, consider the preceding audio as a chunk for transcription
            if silent_chunks:
                start_time, end_time = silent_chunks[0]
                audio_chunk = audio_buffer[:start_time]

                # Check if the audio_chunk is at least 0.1 seconds long
                if len(audio_chunk) >= 100:  # 100 milliseconds = 0.1 seconds
                    # Send audio_chunk for transcription
                    audio_chunk.export("temp_chunk.wav", format="wav")
                    with open("temp_chunk.wav", "rb") as audio_file:
                        transcript = openai.Audio.transcribe("whisper-1", audio_file)
                        print(transcript["text"])

                # Clear the buffer up to the detected silence
                audio_buffer = audio_buffer[end_time:]



if __name__ == "__main__":
    stream_id = ''


    #TestStreamSpeakers(stream_id=stream_id)
    TranscribeStreamWithWhisper(stream_id=stream_id)
