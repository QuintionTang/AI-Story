# AI 推理库
from huggingface_hub import InferenceClient
from langchain import HuggingFaceHub

# 配置文件
from config import (HUGGING_FACE_API_TOKEN)

import os
import datetime


hfApiToken = HUGGING_FACE_API_TOKEN

# 仅 HuggingFace Hub 推论
model_Image2Text = "Salesforce/blip-image-captioning-base"

def imageToText(url):
    from huggingface_hub import InferenceClient
    client = InferenceClient(token=hfApiToken)
    # 来自huggingface.co/tasks
    text = client.image_to_text(url,model=model_Image2Text)
    print(text)
    return text

# Langchain 到 HuggingFace 的推论
def LC_TextGeneration(model, basetext):
    from langchain import PromptTemplate, LLMChain
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = hfApiToken
    llm = HuggingFaceHub(repo_id=model , model_kwargs={"temperature":0.45,"min_length":30, "max_length":250})
    print(f"Running repo: {model}")    
    print("Preparing template")
    template = """<human>: write a very short story about {basetext}.
    The story must be a one paragraph.
    <bot>: """
    prompt = PromptTemplate(template=template, input_variables=["basetext"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    start = datetime.datetime.now() 
    print("Running chain...")
    story = llm_chain.run(basetext)
    stop = datetime.datetime.now()  
    elapsed = stop - start
    print(f"Executed in {elapsed}")
    print(story)
    return story
    
def  text2speech(text):
  import requests
  API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
  headers = {"Authorization": f"Bearer {hfApiToken}"}
  payloads = {
      "inputs" : text
  }
  response = requests.post(API_URL, headers=headers, json=payloads)
  with open('audio.flac', 'wb') as file:
    file.write(response.content)

basetext = "a boy sitting on top of a pile of books" # imageToText("./images/a-boy.jpg")
model_TextGeneration="togethercomputer/RedPajama-INCITE-Chat-3B-v1"
mystory = LC_TextGeneration(model_TextGeneration, basetext)
print("="*50)
finalstory = mystory.split('\n\n')[0]
print(finalstory)