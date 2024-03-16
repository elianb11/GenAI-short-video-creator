def generate_image_descriptions(openai_client, full_story, paragraphs):
    art_style_response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are an helpful assistant and an expert in art styles."},
            {"role": "user", "content": f"Here is a story: {full_story}\n\nI want to generate pictures with DALL-E model to illustrate this. Propose me an illustration artistic style that could fit the story. Answer only the name of the artistic style."},
        ]
    )
    art_style = art_style_response.choices[0].message.content

    print(f"Art style: {art_style}")

    image_descriptions = []
    for elem in paragraphs:
        image_desc_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are an helpful assistant and an expert in scene description."},
                {"role": "user", "content": f"Here is the context: {full_story}\n\nImagine and generate a short scene description that could illustrate the following part of the text: {elem}\n\nDo not include explicit content, your answer will be read by teenagers."},
            ]
        )
        final_desc = f"Use the following artistic style: {art_style}. Illustrate the following scene: {image_desc_response.choices[0].message.content}"
        image_descriptions.append(final_desc)

    print(image_descriptions)

    return image_descriptions