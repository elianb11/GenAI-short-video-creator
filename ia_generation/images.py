import requests
import os

def download_image(url, filepath):
    response = requests.get(url)
    if response.status_code == 200:
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print("Image downloaded successfully as", filepath)
    else:
        print("Failed to download image")

def generate_images(openai_client, image_descriptions):

    # Generate the images
    image_urls = []
    i = 0
    for img_desc in image_descriptions:
        i += 1
        image = openai_client.images.generate(
            model="dall-e-3",
            prompt=img_desc,
            size="1024x1792",
            quality="standard",
            n=1,
        )
        image_urls.append(image.data[0].url)
        print(f"Image #{i} generated successfully")

    i = 0
    for url in image_urls:
        i += 1
        filepath = f"/tmp/generated_images/image{i}.jpg"
        download_image(url, filepath)