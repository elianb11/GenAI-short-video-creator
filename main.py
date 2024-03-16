from openai import OpenAI
import json

from moviepy.config import change_settings
from dotenv import load_dotenv

from ia_generation.image_descriptions import generate_image_descriptions
from ia_generation.images import generate_images
from ia_generation.stories import generate_story
from ia_generation.voices import generate_voices
from video_editing.clips_manager import create_video

# for windows system only
# change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

load_dotenv()

def main():
    client = OpenAI()

    stories = []
    # Create first a list of events (in JSON format) you want to create a story about
    with open("/local/stories.json", 'r') as f:
        stories.extend(json.load(f))

    for story_event in stories:

        full_story, paragraphs = generate_story(client, story_event)

        image_descriptions = generate_image_descriptions(client, full_story, paragraphs)

        generate_images(client, image_descriptions)

        generate_voices(client, paragraphs)

        create_video()


if __name__ == '__main__':
    main()
