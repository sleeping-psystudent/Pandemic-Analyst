import google.generativeai as genai

def input_API(api):
    genai.configure(api_key=api)
    model = genai.GenerativeModel('gemini-pro')
    try:
        model.generate_content(
        "test",
        )
        print("Set Gemini API sucessfully!!")
        return model
    except:
        print("There seems to be something wrong with your Gemini API. Please follow our demonstration in the slide to get a correct one.")
        return None