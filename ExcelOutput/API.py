import google.generativeai as genai
import time

def input_API(api):
    genai.configure(api_key=api)
    model = genai.GenerativeModel('gemini-pro')
    while(True):
        try:
            model.generate_content(
            "test",
            )
            print("Set Gemini API sucessfully!!")
            return model
        except:
            print("There seems to be something wrong with your Gemini API.")
            time.sleep(5)