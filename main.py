# 使用 Streamlit 进行 HuggingFace 推理的 Python 应用程序
# AI 推理库
from huggingface_hub import InferenceClient
from langchain import HuggingFaceHub
import requests
# 内部使用
import os
import datetime
import uuid
# STREAMLIT
import streamlit as st
# 配置文件
from config import (HUGGING_FACE_API_TOKEN)

hfApiToken = HUGGING_FACE_API_TOKEN
# 只有HuggingFace Hub 推理

model_TextGeneration="togethercomputer/RedPajama-INCITE-Chat-3B-v1"
model_Image2Text = "Salesforce/blip-image-captioning-base"
model_Text2Speech="espnet/kan-bayashi_ljspeech_vits"

def imageToText(url):
    from huggingface_hub import InferenceClient
    client = InferenceClient(token=hfApiToken)
    model_Image2Text = "Salesforce/blip-image-captioning-base"
    text = client.image_to_text(url,
                                model=model_Image2Text)
    print(text)
    return text


def  text2speech(text):
  import requests
  API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
  headers = {"Authorization": f"Bearer {hfApiToken}"}

  payloads = {
      "inputs" : "".join(text.split('\n\n'))
  }
  response = requests.post(API_URL, headers=headers, json=payloads)
  with open('audiostory.flac', 'wb') as file:
    file.write(response.content)


# Langchain 到 Hugging Face 的推理
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

def generate_uuid():
    return uuid.uuid4().hex

def main():

  st.set_page_config(page_title="Your Photo Story Creatror App", page_icon='📱')

  st.header("Turn your Photos into Amazing Audio Stories")
  st.image('./assets/banner.jpg', use_column_width=True)
  st.markdown("1. Select a photo from your pc\n 2. AI detect the photo description\n3. AI write a story about the photo\n4. AI generate an audio file of the story")
  
  image_file = st.file_uploader("Choose an image...", type=['png', 'jpg'] )
  if image_file is not None:
    print(image_file)
    bytes_data = image_file.getvalue()
    save_name = generate_uuid()
    upload_path = f"./upload/{save_name}.jpg"
    with open(upload_path, "wb") as file:
      file.write(bytes_data)
    st.image(image_file, caption="Uploaded Image...",
             use_column_width=True)
    
    st.warning("Generating Photo description",  icon="🤖")
    basetext = imageToText(upload_path)
    with st.expander("Photo Description"):
      st.write(basetext)    
    st.warning("Generating Photo Story",  icon="🤖")
    mystory = LC_TextGeneration(model_TextGeneration, basetext)
    finalstory = mystory
    print("="*50)
    with st.expander("Photo Story"):
      st.write(finalstory)    
    st.warning("Generating Audio Story",  icon="🤖")
    text2speech(finalstory)
    

    st.audio('audiostory.flac')
    st.success("Audio Story completed!")


if __name__ == '__main__':
   main()