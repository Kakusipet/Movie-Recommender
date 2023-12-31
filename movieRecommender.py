import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")
movie_key=os.getenv("OMDB_API_KEY")
genai.configure(api_key=api_key)

# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)
model = genai.GenerativeModel('gemini-pro')

#response = model.generate_content("What is the meaning of life?")
#print (response.text)

def gpt_function(instruction):
    data = {
        "contents": {
            "role": "user",
            "parts": {
                "text": instruction
            }
        },
        "tools" : [
            {
                "function_declarations": [
                    {
                        "name": "find_movie_title",
                        "description": "Get the title of the movie without any additional information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Movie title without year"
                                },

            },
            "required": [
              "title"
            ]
          }
        },
                ]
            }
        ]
        
    }
    #title = data["tools"][0]["function_declarations"][0]["parameters"]["properties"]["title"]
    response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}", json=data)
    result = response.json()

    if "candidates" not in result:
        print("Error locating movie")

    try:
        if "functionCall" in result["candidates"][0]["content"]["parts"][0]:
            return result["candidates"][0]["content"]["parts"][0]["functionCall"]["args"]["title"]
    except (KeyError, IndexError):
        raise ValueError("Error occurred while extracting title from the result.")

    # return result["candidates"][0]["content"]["parts"][0]["functionCall"]["args"]["title"]
    # #return title
    # #return data

st.title("Movie Recommender")

input = st.text_input("", placeholder="Suggest a movie made in the 2000s related to zombies")
button = st.button("Recommend")

def get_details(title):
    return requests.post(f"https://www.omdbapi.com/?apikey={movie_key}&t={title}").json()

if button:
    response2 = model.generate_content("Give me the movie that is most closely related to the following input and if there are not related movies then decline to provide any recommendations: " + input)
    print(response2.text)
    title = gpt_function(response2.text)
    st.write(title)
    st.image(get_details(title)["Poster"])
    st.write(get_details(title)["Plot"])

