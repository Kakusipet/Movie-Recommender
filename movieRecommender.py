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
                        "description": "Get the titles of the movies without including ANY other information such as year or serial number.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "array",
                                    "description": "list of movie titles without year"
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
            if result["candidates"][0]["content"]["parts"][0]["functionCall"]["args"]["title"] != None:
                print (result["candidates"][0]["content"]["parts"][0]["functionCall"]["args"])
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
    #print(response2.text)
    titles = gpt_function(response2.text)
    print(titles)
    # st.write(title)
    # st.image(get_details(title)["Poster"])
    # st.write(get_details(title)["Plot"])
    try:
        cols = st.columns(len(titles))  # Create columns for grid layout
    except Exception as e:
        print(e)
        st.header("Something went wrong. Please try again.")
        os._exit(0)
    i=0
    for col in cols:
        try:
            movie_details = get_details(titles[i])  # Replace with the desired title
            poster_url = movie_details["Poster"]
            with col:
                st.image(poster_url, width=150)
                st.write(movie_details["Plot"])
        except Exception as e:
            print(e)
        i=i+1    

    # for i, title in enumerate(titles):
    #     with cols[i]:
    #         try:
    #             movie_details = get_details(title)
    #             st.image(movie_details["Poster"], width=150)  # Adjust width as needed
    #             st.markdown(f"**{title}**")
    #             st.write(movie_details["Plot"])
    #         except Exception as e:
    #             st.error(f"Error fetching details for {title}: {e}")

    # for title in titles:
    #         # st.write(title)
    #         try:
    #             movie_details = get_details(title)
    #             st.image(movie_details["Poster"])
    #             st.write(movie_details["Plot"])
    #             st.markdown("---")  # Add separator between movies
    #         except Exception as e:
    #             st.error(f"Error fetching details for {title}: {e}")
