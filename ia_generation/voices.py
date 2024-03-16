import whisper
import json
import os

def generate_voices(openai_client, paragraphs):

    # Generate the voice recordings
    i = 0
    for paragraph in paragraphs:
        i += 1
        speech_file_path = f"/tmp/generated_voices/speech{i}.mp3"
        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=paragraph
        )
        response.stream_to_file(speech_file_path)
        print(f"Speech #{i} generated successfully")

    # Get the words timestamps for each audio
    mp3_dir = '/tmp/generated_voices'
    mp3_files = sorted([os.path.join(mp3_dir, f) for f in os.listdir(mp3_dir) if f.endswith('.mp3')])

    model = whisper.load_model("medium")
    timestamps = []
    for i, mp3 in enumerate(mp3_files):
        result = model.transcribe(mp3, word_timestamps=True)
        word_level_info = []
        for elem in result['segments']:
            words = elem['words']
            for word in words:
                word_level_info.append({'word': word['word'].strip(), 'start': word['start'], 'end': word['end']})
        timestamps.append(word_level_info)

    for i, timestamp in enumerate(timestamps):
        filepath = f'/tmp/word_timestamps/timestamp{i}.json'
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'w') as f:
            json.dump(timestamp, f)