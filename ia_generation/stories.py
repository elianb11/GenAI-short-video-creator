PARAGRAPHS_NB = 4
WORDS_MAX_NB = 200

def generate_story(openai_client, story_event):
    # Generate the script text
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are an expert in story-telling."},
            {"role": "user", "content": f"Create an appealing story based on the following event: {story_event}\n\nAdd suspense to the story to make it attractive. The story must include less than {WORDS_MAX_NB} words and exactly {PARAGRAPHS_NB} paragraphs."},
        ]
    )

    paragraphs = response.choices[0].message.content.split("\n\n")

    print(paragraphs)

    if len(paragraphs) != PARAGRAPHS_NB:
        raise Exception("Number of paragraphs is not equal to PARAGRAPHS_NB.")
    
    return response.choices[0].message.content, paragraphs