import openai

# Set your OpenAI API key
openai.api_key = "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"

def translate_text(text, source_language):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a {source_language} speaker."},
            {"role": "user", "content": text},
            {"role": "system", "content": f"Translate the following {source_language} text into English."},
        ],
        max_tokens=200
    )

    translated_text = response["choices"][0]["message"]["content"]
    return translated_text

def generate_summary(reviews,max_tokens=200):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summary of customer reviews:"},
            {"role": "user", "content": reviews},
            {"role": "system", "content": "Generate a summary highlighting the important points."},
        ],
        max_tokens=max_tokens
    )

    return response["choices"][0]["message"]["content"]

def find_answers(review, question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Customer review: {review}"},
            {"role": "user", "content": question},
            {"role": "system", "content": "Provide crisp answers & insights based on the reviews provided in a positive tone and highlight the facts & area to be focused in a subtle way."},
        ],
        max_tokens=100
    )
    return response['choices'][0]['message']['content']