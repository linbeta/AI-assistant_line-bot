from dotenv import load_dotenv
from flask import Flask, request, abort
from dotenv import load_dotenv
import openai
import os
from translate import Translate

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)
# 載入.env檔案中的環境變數
load_dotenv()

# 取得.env檔案中的環境變數
line_channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
line_channel_secret = os.getenv('LINE_CHANNEL_SECRET')
openai_key = os.getenv('OPENAI_API_KEY')

configuration = Configuration(access_token=line_channel_access_token)
handler = WebhookHandler(line_channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

translator = Translate(openai_key)
test = translator.translate_text("我來測試一下內容")

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_msg = event.message.text
        reply_content = event.message.text
        if user_msg == "翻譯工具":
            reply_content = "請動翻譯工具模式，創建一個翻譯工具物件，直到user給出結束指令\n" + test
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_content)]
            )
        )

if __name__ == "__main__":
    app.run(debug=True)
