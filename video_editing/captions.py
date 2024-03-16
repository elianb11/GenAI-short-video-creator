from moviepy.editor import *
import json


def create_caption(text_json):
    wordcount = len(text_json['textcontents'])
    full_duration = text_json['end'] - text_json['start']

    word_clips = []
    xy_textclips_positions = []

    x_pos = 0
    y_pos = 0
    frame_width = 1024
    frame_height = 1792
    x_buffer = frame_width * 1 / 12
    y_buffer = frame_height * 3 / 5
    space_width = 16

    color = 'white'
    active_color = 'cyan'
    font_size = 80
    font = 'Impact'
    stroke_color = 'black'
    stroke_width = 4.5

    for index, wordJSON in enumerate(text_json['textcontents']):
        duration = wordJSON['end'] - wordJSON['start']
        word_clip = TextClip(
            wordJSON['word'],
            font=font,
            fontsize=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width
        ).set_start(text_json['start']).set_duration(full_duration)
        word_width, word_height = word_clip.size
        if x_pos + word_width + space_width > frame_width - 2 * x_buffer:
            # Move to the next line
            x_pos = 0
            y_pos = y_pos + word_height + 12
            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos": x_pos + x_buffer,
                "y_pos": y_pos + y_buffer,
                "width": word_width,
                "height": word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })
            word_clip = word_clip.set_position((x_pos + x_buffer, y_pos + y_buffer))
            x_pos = word_width + space_width
        else:
            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos": x_pos + x_buffer,
                "y_pos": y_pos + y_buffer,
                "width": word_width,
                "height": word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })
            word_clip = word_clip.set_position((x_pos + x_buffer, y_pos + y_buffer))
            x_pos = x_pos + word_width + space_width
        word_clips.append(word_clip)

    for highlight_word in xy_textclips_positions:
        word_clip_highlight = TextClip(
            highlight_word['word'],
            font=font,
            fontsize=font_size,
            color=active_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width
        ).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
        word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
        word_clips.append(word_clip_highlight)

    return word_clips


def split_text_into_lines(data):
    max_chars = 50
    # max duration in seconds
    max_duration = 2.5
    # Split if nothing is spoken (gap) for these many seconds
    max_gap = 1.0

    subtitles = []
    line = []
    line_duration = 0

    for idx, word_data in enumerate(data):
        word_data["word"] = word_data["word"].upper()
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start

        temp = " ".join(item["word"] for item in line)

        # Check if adding a new word exceeds the maximum character count or duration
        new_line_chars = len(temp)

        duration_exceeded = line_duration > max_duration
        chars_exceeded = new_line_chars > max_chars
        if idx>0:
            gap = word_data['start'] - data[idx-1]['end']
            # print (word,start,end,gap)
            max_gap_exceeded = gap > max_gap
        else:
            max_gap_exceeded = False

        if duration_exceeded or chars_exceeded or max_gap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0

    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)

    return subtitles

def generate_line_level_timestamps():
    # Convert word-level timestamps JSON to line-level timestamps JSON
    word_level_timestamps_dir = "/tmp/word_timestamps"
    word_level_timestamp_files = sorted(
        [os.path.join(word_level_timestamps_dir, f) for f in os.listdir(word_level_timestamps_dir) if
            f.endswith('.json')])

    word_level_timestamps = []
    for word_level_timestamp_path in word_level_timestamp_files:
        with open(word_level_timestamp_path, 'r') as f:
            word_level_timestamps.append(json.load(f))

    line_level_timestamps = []
    for i, timestamp in enumerate(word_level_timestamps):
        line_timestamp = split_text_into_lines(timestamp)
        line_level_timestamps.append(line_timestamp)
        filepath = f'/tmp/line_timestamps/timestamp{i}.json'
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'w') as f:
            json.dump(line_timestamp, f)