import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

app = Flask(__name__)


# Line API credentials
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

# OpenAI API credentials
gpt_api_key = os.getenv("OPENAI_API_KEY")

# Function to send a message to OpenAI GPT API
def get_gpt_response(prompt):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {gpt_api_key}'
    }
    data = {
        'prompt': prompt,
        'temperature': 0.7,
        'max_tokens': 50
    }
    response = requests.post('https://api.openai.com/v1/engines/davinci-codex/completions', headers=headers, json=data)
    return response.json()['choices'][0]['text']

# Handle Line messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    gpt_response = get_gpt_response(user_input)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=gpt_response))


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)