import ffmpeg
import time
from moviepy.editor import *
from easing_functions import *
from mutagen.mp3 import MP3
import json

from video_editing.captions import create_caption
       
def create_video():
    # Video creation and editing
    mp3_dir = '/tmp/generated_voices'
    mp3_files = sorted([os.path.join(mp3_dir, f) for f in os.listdir(mp3_dir) if f.endswith('.mp3')])

    durations = []
    for mp3_file in mp3_files:
        duration = get_mp3_duration(mp3_file)
        if duration is not None:
            print(f"Duration of {mp3_file}: {duration}sec")
            durations.append(duration)
        else:
            print("Error")

    image_folder = '/tmp/generated_images'
    audio_folder = '/tmp/generated_voices'

    # Get image paths
    image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".jpg")])

    # Get audio paths
    audio_files = sorted(
        [os.path.join(audio_folder, audio) for audio in os.listdir(audio_folder) if audio.endswith(".mp3")])

    # Load audio clips
    audio_clips = [AudioFileClip(audio) for audio in audio_files]

    # Create video clips
    clips = [ImageClip(image, duration=duration) for image, duration in zip(image_files, durations)]

    min_scale = 1.0
    max_scale = 1.2

    # Add zoom-in animation for each clip and set audio
    for i, clip in enumerate(clips):
        ease = ExponentialEaseOut(start=min_scale, end=max_scale, duration=durations[i])
        clip = clip.resize(ease)
        clip = clip.fadein(0.5)
        clip = clip.fadeout(0.5)
        if i < len(audio_clips):
            duration = min(clip.duration, audio_clips[i].duration)
            clip = clip.set_audio(audio_clips[i].subclip(0, duration))
        else:
            clip = clip.set_audio(None)
        clips[i] = clip

    line_timestamps_dir = "/tmp/line_timestamps"
    line_timestamp_files = sorted(
        [os.path.join(line_timestamps_dir, f) for f in os.listdir(line_timestamps_dir) if f.endswith('.json')])

    line_level_timestamps = []
    for line_timestamp_path in line_timestamp_files:
        with open(line_timestamp_path, 'r') as f:
            line_level_timestamps.append(json.load(f))

    for i, line_level_timestamp in enumerate(line_level_timestamps):
        print(f"Adding text on clip #{i}...")
        all_line_level_splits = []
        for line in line_level_timestamp:
            out = create_caption(line)
            all_line_level_splits.extend(out)

        clips[i] = CompositeVideoClip([clips[i]] + all_line_level_splits)

    final_clip = concatenate_videoclips(clips, method="compose")
    current_timestamp = int(time.time())
    output_mp4_path = f"/output_videos/mp4/video{current_timestamp}.mp4"
    output_mov_path = f"/output_videos/mov/video{current_timestamp}.mov"
    directory = os.path.dirname(output_mp4_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory = os.path.dirname(output_mov_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    final_clip.write_videofile(output_mp4_path, fps=24)
    ffmpeg.input(output_mp4_path).output(output_mov_path).run()


def get_mp3_duration(file_path):
    try:
        audio = MP3(file_path)
        duration_in_seconds = audio.info.length
        return duration_in_seconds
    except Exception as e:
        print("An error occurred:", e)
        return None