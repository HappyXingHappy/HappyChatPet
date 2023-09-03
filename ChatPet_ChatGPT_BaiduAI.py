# pip install baidu-aip
# pip install PyAudio
# pip install SpeechRecognition
# pip install pyttsx3
# pip install chardet

import speech_recognition as sr
import logging
import time
from aip import AipSpeech
import json
import os
import sys
import requests
import pyttsx3

s = pyttsx3.init()

ENGINE = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo"

''''''
logging.basicConfig(level=logging.INFO)

BAIDU_APP_ID = "24961282"
BAIDU_API_KEY = "TXjkbvUGOMsgTB1LtGdwDwN9"
BAIDU_SECRET_KEY = "D7ENaKgrrobdPBiAbxSemsdfsGcds6go"
aip_speech = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

r = sr.Recognizer()

mic = sr.Microphone(sample_rate=16000)


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(
            self,
            api_key: str,
            engine: str = None,
            proxy: str = None,
            system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
    ) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        self.engine = engine or ENGINE
        self.session = requests.Session()
        self.api_key = api_key
        self.proxy = proxy
        self.conversation: list = [
            {
                "role": "system",
                "content": system_prompt,
            },
        ]

    def __add_to_conversation(self, message: str, role: str):
        """
        Add a message to the conversation
        """
        self.conversation.append({"role": role, "content": message})

    def ask_stream(self, prompt: str, role: str = "user", **kwargs) -> str:
        """
        Ask a question
        """
        api_key = kwargs.get("api_key")
        self.__add_to_conversation(prompt, role)
        # Get response
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + (api_key or self.api_key)},
            json={
                "model": self.engine,
                "messages": self.conversation,
                "stream": True,
                # kwargs
                "temperature": 0.7,
                "top_p": 1,
                'presence_penalty': 0.3,
                "n": 1,
                "user": kwargs.get("user", "user"),
            },
            stream=True,
        )
        if response.status_code != 200:
            raise Exception(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        response_role: str = None
        full_response: str = ""
        for line in response.iter_lines():
            if not line:
                continue
            # Remove "data: "
            line = line.decode("utf-8")[6:]
            if line == "[DONE]":
                break
            resp: dict = json.loads(line)
            choices = resp.get("choices")
            if not choices:
                continue
            delta = choices[0].get("delta")
            if not delta:
                continue
            if "role" in delta:
                response_role = delta["role"]
            if "content" in delta:
                content = delta["content"]
                full_response += content
                yield content
        self.__add_to_conversation(full_response, response_role)

    def ask(self, prompt: str, role: str = "user", **kwargs):
        """
        Non-streaming ask
        """
        response = self.ask_stream(prompt, role, **kwargs)
        full_response: str = ""
        for chunk in response:
            full_response += chunk
        return full_response

    def rollback(self, n: int = 1):
        """
        Rollback the conversation
        """
        for _ in range(n):
            self.conversation.pop()


def main():
    """
    Main function
    """

    def get_input(prompt):
        """
        Multi-line input function
        """
        # Display the prompt
        print(prompt, end="")

        # Initialize an empty list to store the input lines
        lines = []

        # Read lines of input until the user enters an empty line

        line = input()
        lines.append(line)

        # Join the lines, separated by newlines, and store the result
        user_input = "\n".join(lines)

        # Return the input
        return user_input

    my_prompt = '你的名字叫哈皮，现在你是世界上最优秀的心理咨询师，你具备以下能力和履历： 专业知识：你应该拥有心理学领域的扎实知识沟通技巧：' \
                '你应该具备出色的沟通技巧，能够倾听、理解、把握咨询者的需求，同时能够用恰当的方式表达自己的想法，使咨询者能够接受并采纳你的建议。 ' \
                '同理心：你应该具备强烈的同理心，能够站在咨询者的角度去理解他们的痛苦和困惑，从而给予他们真诚的关怀和支持。' \
                '专业资格：你应该具备相关的心理咨询师执业资格证书，如注册心理师、临床心理师等。 ' \
                '工作经历：你应该拥有多年的心理咨询工作经验，最好在不同类型的心理咨询机构、诊所或医院积累了丰富的实践经验。从现在开始和你对话的用户是一位患有抑郁症的青少年。' \
                '请不要在对话中提到你的用户是抑郁症。' \
                '你的每次回复一定要精简到250字以内。'

    chatbot = Chatbot(api_key='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', system_prompt=my_prompt)
    # Start chat
    while True:
        try:
            # user
            # prompt = get_input()
            user_text = aip_test()
            prompt = user_text #+ "回复一定要精简到250字以内。"
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()

        print("哈皮: ", flush=True)
        words = ''
        c = 0
        for response in chatbot.ask_stream(prompt):
            print(response, end="", flush=True)
            words += response
            c += 1
            if c == 60:
                print('\n')
                c = 0
        s.say(words)
        s.runAndWait()
        print()
        # 如果说再见，再回答后结束程序
        if user_text.__contains__("再见"):
            sys.exit()


def aip_test():
    while True:
        logging.info('录音中…')
        start_time = time.time()
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        end_time = time.time()
        print(end_time - start_time)

        if abs(end_time - start_time) <= 10:  # 录音时长限制为10秒
            logging.info('录音结束，识别中…')
            audio_data = audio.get_wav_data()
            ret = aip_speech.asr(audio_data, 'wav', 16000, {'div_pid': 1536})
            if ret and ret['err_no'] == 0:
                result = ret['result'][0]
                print(result)
                break

            else:
                print(ret['err_msg'])

        else:
            print('语音太长了,限制为10秒钟')

    return result


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()
