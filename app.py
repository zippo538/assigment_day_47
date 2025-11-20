import streamlit as st 
import base64
import getpass
import json 
import os 
from dotenv import load_dotenv 
import re
import pandas as pd
from PIL import Image


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage 
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

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




def load_google_api(api_key: str) -> ChatGoogleGenerativeAI:
    try : 
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.0,api_key=api_key)
        return llm
    except Exception as e : 
        st.error(f"Error load api {str(e)}")


def image_to_bs64(image : object)-> str:
    encoded =base64.b64encode(image).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{encoded}"
    return data_uri

def response_llm(prompt, data_image, llm : ChatGoogleGenerativeAI) :
    message = HumanMessage(
        content= [
        {"type" : "text","text" : prompt},
        {"type" : "image_url", "image_url" : data_image}
        ]
    ) 
    response = llm.invoke([message])
    return response

def clean_json(msg : str) :
    clean = re.sub(r"```(?:json)?", "", msg).strip() 
    data = json.loads(clean)
    return data 

def df_to_json(data : list):
    df = pd.DataFrame(data)
    return df

def resize_to_height(image: Image.Image, target_height: int = 480) -> Image.Image:
    width, height = image.size
    aspect_ratio = width / height
    new_width = int(target_height * aspect_ratio)
    resized_image = image.resize((new_width, target_height), Image.Resampling.LANCZOS)
    return resized_image


    
    

st.title("Invoice Extractor and Split Bill")
st.set_page_config(layout="wide") 

uploaded_file = st.file_uploader("upload Invoice image",type=['png','jpg','jpeg'])
total_bil = 0.0

try : 
    if uploaded_file:
        #get json image
        with st.spinner('Get Image Text'):
            image_bytes = uploaded_file.read()
            image_to_64 = image_to_bs64(image_bytes)
            google_api = load_google_api(google_api_key)    
            response = response_llm(PROMPT,image_to_64,google_api)
        
        
        msg = response.content
        data = clean_json(msg)
        
        #total bil        
        total_bil = float(data['total'])
        st.success(f"Total tagihan anda : Rp.{total_bil:.2f}")
        
        st.markdown("#### Your Receipt Data")
        col1, col2 =  st.columns([3,7])
        with col1:
            #image preview
            image= Image.open(uploaded_file)
            st.image(resize_to_height(image))
        
        with col2:
            #menus
            df = df_to_json(data['menus'])
            st.dataframe(df,use_container_width = True,hide_index=True)
        
        
        people_input = st.text_input("Masukkan nama orang (dipisah koma, contoh: Alice, Bob, Charlie):")
        people = [name.strip() for name in people_input.split(',') if name.strip()]
        
        if people :
            st.markdown("### Split bill item ")
            assignments= {}
            for person in people :
                assignments[person] = []
            
            num_cols = 2
            cols = st.columns(num_cols) 
            
            for i, item in enumerate(data['menus']):
                col = cols[i % num_cols]
                with col : 
                    st.write(f"**{item['name']} - Rp.{item['price']:.2f} ({item['count']})**")
                    assigned_person = st.selectbox(f"Assign ke orang untuk {item['name']}:", ["Tidak assign"] + people, key=f"assign_{item['name']}")
                    if assigned_person != "Tidak assign":
                        assignments[assigned_person].append(item['price'])
        
            # Input persentase tip (opsional)
            tip_percentage = st.slider("Persentase tip (%):", min_value=0, max_value=100, value=0)

            # Hitung total per orang
            tip_total = total_bil * (tip_percentage / 100)
            tip_per_person = tip_total / len(people) if people else 0

            st.markdown("### Ringkasan Pembagian")
            summary = []
            for person, items in assignments.items():
                person_total = sum(items) + tip_per_person
                summary.append({"Orang": person, "Total Item": sum(items), "Tip": tip_per_person, "Total Bayar": person_total})

            st.dataframe(pd.DataFrame(summary,use_container_width = True,hide_index=True))

        
        
except Exception as e: 
    st.error(f"File Error Uploded : {str(e)}")



        
    
    
    
    
    
    
    
        
        
        
    

        
        
        
        
  
