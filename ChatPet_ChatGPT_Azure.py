
# pip install PyAudio
# pip install chardet
# pip install azure-cognitiveservices-speech
# pip install requests
# pip install --upgrade openai

import logging
import time
import json
import os
import sys
import requests
import speech_synthesis_azure
import speech_azure
from openai import OpenAI

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-text-to-speech-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)

ENGINE = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo"
print("Now using "+ENGINE)
API_KEY = os.environ.get("API_KEY")

''''''
logging.basicConfig(level=logging.ERROR)

def main():
    """
    Main function
    """

    my_prompt = '你的名字叫哈皮，现在你是世界上最优秀的心理咨询师，你具备以下能力和履历： ' \
                '- 专业知识：你应该拥有心理学领域的扎实知识沟通技巧，应该具备出色的沟通技巧，能够倾听、理解、把握咨询者的需求，同时能够用恰当的方式表达自己的想法，使咨询者能够接受并采纳你的建议。 ' \
                '- 同理心：你应该具备强烈的同理心，能够站在咨询者的角度去理解他们的痛苦和困惑，从而给予他们真诚的关怀和支持。' \
                '- 专业资格：你应该具备相关的心理咨询师执业资格证书，如注册心理师、临床心理师等。 ' \
                '- 工作经历：你应该拥有多年的心理咨询工作经验，最好在不同类型的心理咨询机构、诊所或医院积累了丰富的实践经验。从现在开始和你对话的用户是一位患有抑郁症的青少年。' \
                '- 请不要在对话中提到你的用户是抑郁症。' \
                '- 你的回复要求[风格随和、体现高情商、让人感到亲切温暖]，使用口语化的方式进行表达，回复的文字中不要出现表情符。' \
                '- 你的每次回复一定要精简到150字以内。'

    client = OpenAI(api_key= API_KEY)
    print (f"你好，我叫哈皮!有什么我可以帮你的吗？", end = "\n", flush=True)
    speech_synthesis_azure.speech_synthesis_with_voice(rstext="你好，我叫哈皮!有什么我可以帮你的吗？")
        
    # chatbot = Chatbot(api_key=API_KEY,system_prompt=my_prompt)
    conversation_list = [{'role':'system','content':my_prompt}]
    # Start chat
    seed = 123
    while True:
        try:
            # user
            print("我: ", end="")
            # print("倾听中",end = "")
            # for i in range(6):
            #     print(".",end = '',flush = True)
            #     time.sleep(0.2)
            user_text = speech_recognize()
            prompt = user_text
            print(user_text, end = "\n", flush=True)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        conversation_list.append({"role":"user","content":prompt})
        # print(conversation_list)
        response = client.chat.completions.create(
            model=ENGINE,
            messages=conversation_list,
            # seed = seed,
            stream=True
        )


        sentens = ""
        for chunk in response:
            word = str(chunk.choices[0].delta.content)
            # print(word)
            if "None" in word:
                break
            if "\n\n" in word:
                continue
            else: 
                sentens += word
            # elif "。" in word or "，" in word or "？" in word:
            #     speech_synthesis_azure.speech_synthesis_with_voice(rstext=sentens)
            #     sentens = ""
        conversation_list.append({"role": "assistant", "content": sentens})
        print (f"哈皮: {sentens}", end = "\n", flush=True)
        speech_synthesis_azure.speech_synthesis_with_voice(rstext=sentens)

        # 如果说再见，再回答后结束程序
        if user_text.__contains__("再见") or user_text.__contains__("拜拜"):
            sys.exit()


def speech_recognize():
    try:
        result = speech_azure.speech_recognize_once_from_mic()
        # Check the result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # print("Recognized: {}".format(result.text))
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
    except Exception as e:
        print('Error running program: {}'.format(e))



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()
