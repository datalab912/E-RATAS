from flask import Flask, request
import asyncio
from IPython.display import display, HTML
from openai import OpenAI
client = OpenAI()

GPT_MODEL = "gpt-3.5-turbo"
REQUEST_SEED = 42 

app = Flask(__name__)

message_history = []

@app.route("/")
def hello_world():
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ])
    return completion.choices[0].message.content

@app.route("/chat", methods=["POST"])
def chat():
    paragraph = request.json["paragraph"]
    title = request.json["title"]
    
    prompt = f"""
    Given this paragraph:  \
    {paragraph} \
    And the title: {title} \
    As a language model, give the percentage of how much the paragraph describe the title
    """
    message_history.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model=GPT_MODEL,
        messages=message_history,
        seed = REQUEST_SEED
    )
    content = completion.choices[0].message.content
    
    message_history.append({"role": "system", "content": content})
    print('completion', completion)
    return content

@app.route('/query', methods=["POST"])
def get_chat_response(temperature: float = 0.7
):
    try:
        paragraph = request.json["paragraph"]
        title = request.json["title"] 
        prompt = f"Given this paragraph: \n{paragraph}\nAnd the title: {title}\nAs a language model, give the percentage of how much the paragraph describe the title. Please use the following scale: 0-100. Answer with the number only"
        message_history.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=message_history,
            seed=REQUEST_SEED,
            max_tokens=200,
            temperature=temperature,
        )

        response_content = response.choices[0].message.content
        system_fingerprint = response.system_fingerprint
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.total_tokens - response.usage.prompt_tokens
        message_history.append({"role": "system", "content": response_content})

        table = f"""
        <table>
        <tr><th>Response</th><td>{response_content}</td></tr>
        <tr><th>System Fingerprint</th><td>{system_fingerprint}</td></tr>
        <tr><th>Number of prompt tokens</th><td>{prompt_tokens}</td></tr>
        <tr><th>Number of completion tokens</th><td>{completion_tokens}</td></tr>
        </table>
        """
        display(HTML(table))

        return table
    except Exception as e:
        print(f"An error occurred: {e}")
        return None