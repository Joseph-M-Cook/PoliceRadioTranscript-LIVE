import requests
import openai
import vlc
from pydub.playback import play
from pydub import AudioSegment, silence
import time

# Initialize OpenAI API
openai.api_key = ''

def TestStreamSpeakers(stream_id):
    '''
    This function tests the Broadcastify stream endpoint on
    machines speakers through VLC. Purposed for debugging
    and testing obfuscated HTTP requests for exposed endpoints.

    :param str stream_id: The stream we are trying to connect to.
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

def TranscribeStreamWithWhisper(stream_id, duration=5):
    '''
    This function captures a segment of a Broadcastify stream for a specified duration, 
    saves it to a file, chunks the audio based on silence, and transcribes each chunk using
    OpenAI's Whisper.

    :param str stream_id: The stream we are trying to connect to.
    :param int duration: Duration in seconds to capture the stream.
    '''

    # Configure streaming source endpoint URL
    stream_url = f'https://broadcastify.cdnstream1.com/{stream_id}'

    # Record the stream using pydub for the specified duration
    stream_data = requests.get(stream_url, stream=True)
    start_time = time.time()
    with open("temp_stream.mp3", "wb") as f:
        for chunk in stream_data.iter_content(chunk_size=1024):
            if time.time() - start_time > duration:
                break
            if chunk:
                f.write(chunk)

    # Convert the recorded stream to wav format
    audio = AudioSegment.from_mp3("temp_stream.mp3")
    audio.export("temp_stream.wav", format="wav")

    # Split the audio into chunks based on silence
    chunks = silence.split_on_silence(audio, silence_thresh=-50.0, min_silence_len=500, keep_silence=100)

    print(len(chunks))
    # Transcribe each chunk using Whisper
    for chunk in chunks:
        chunk.export("temp_chunk.wav", format="wav")
        with open("temp_chunk.wav", "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            text = transcript["text"]
            if text != 'Thanks for watching!':
                print(text)

    # Play the original audio file for comparison
    print("\nPlaying the original audio...")
    play(audio)



if __name__ == "__main__":
    stream_id = ''

    #TestStreamSpeakers(stream_id=stream_id)
    TranscribeStreamWithWhisper(stream_id=stream_id)
