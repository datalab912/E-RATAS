from openai import OpenAI
client = OpenAI()

GPT_MODEL = "gpt-3.5-turbo"
REQUEST_SEED = 42 

def get_chat_response(paragraph: str, title: str, temperature: float = 0.7):
    message_history = []
    prompt = f"Given this paragraph: \n{paragraph}\nAnd the title: {title}\nAs a language model, give the percentage of how much the paragraph describe the title. Please use the following scale: 0-100. Answer with the number only"
    message_history.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=message_history,
        seed=REQUEST_SEED,
        max_tokens=200,
        temperature=temperature,
    )
    return response.choices[0].message.content


with open('paragraph_from_pdf.txt', 'r') as file:
    responses = []
    paragraph_list = file.readlines()[:10]
    title = "Provide a detailed description of the project conducted during the internship and its overall expectations."
    for paragraph in paragraph_list:
        response = get_chat_response(paragraph, title)
        print(response)
        responses.append(response)
        
    with open('paragraph_and_score_gpt.txt', 'a') as file:
        for paragraph, response in zip(paragraph_list, responses):
            file.write(f'{paragraph},{response}\n')