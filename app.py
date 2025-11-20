import streamlit as st 
import base64
import getpass
import json 
import os 
from dotenv import load_dotenv 

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage 
load_dotenv()

google_api_key = os.getenv("AIzaSyC7wHeKb2CjlEz2J7eHLYa1A5EHIze_oJk")

PROMPT= """
You are given an image of a receipt. Please read the content into JSON format:

```
{
    "menus": [
        {
            "name": <item_name>,
            "count": <purchased_count>,
            "price": <total_price>
        },
        ...
    ],
    "total": <total_price_in_receipt>
}
```

return only in JSON format
"""




def load_google_api(api_key: str):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.0,api_key=api_key)
    return llm


def image_to_bs64(image_path: os.path)-> str:
    with open(image_path,"rb") as f:  
        image_bytes = f.read()
    
    encoded =base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{encoded}"
    return data_uri

def generate_json(prompt, data_image, llm : ChatGoogleGenerativeAI) :
    message = HumanMessage(
        content= [
        {"type" : "text","text" : prompt},
        {"type" : "image_url", "image_url" : data_image}
        ]
    ) 
    response = llm.invoke([message])
    return response

st.title("Invoice Extractor and Split Bill")

uploaded_file = st.file_uploader("upload Invoice image",type=['png','jpg','jpeg'])

if uploaded_file:
    save_img = os.path("artifacts",uploaded_file.name)
    with open(save_img,"wb") as f : 
        f.write(uploaded_file.getbuffer())
    
    get_img_path = save_img
    
    image_to_64 = image_to_bs64(get_img_path)
    google_api = load_google_api(google_api_key)
    
    #get json image
    with st.spinner('Get Image Text'):
        invoice_json = generate_json(PROMPT,image_to_64,google_api)
        st.sess
        
        
    

        
        
        
        
  
