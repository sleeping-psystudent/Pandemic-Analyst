import gradio as gr
import google.generativeai as genai
from typing import List, Tuple
import pyperclip
import re

GOOGLE_API_KEY = ""
model = None
disease = ""
country = ""
eleven = ""

# load prompt
with open("translation.txt", "r") as file:
    trans_prompt = file.read()
with open("interaction.txt", "r") as file:
    interact_risk = file.read()
with open("evaluation.txt", "r") as file:
    eval_prompt = file.read()
with open("assessment.txt", "r") as file:
    assess_prompt = file.read()


# update global api
def input_API(api):
    global GOOGLE_API_KEY
    global model

    GOOGLE_API_KEY = api
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    try:
        model.generate_content(
        "test",
        )
        print("Set Gemini API sucessfully!!")
    except:
        print("There seems to be something wrong with your Gemini API. Please follow our demonstration in the slide to get a correct one.")


# clear the article input
def clear() -> List:
    return None

"""
# extract the numbers
def extract(text):
    pattern = r'Assessment Criteria(.*?)Special Circumstances'
    matches = re.findall(pattern, text, re.DOTALL)

    total_score = 0
    for match in matches:
        numbers = re.findall(r': (\d+)', match)
        for num in numbers:
            total_score += int(num)
    
    return total_score
"""

# extract country and disease
def extract_country_disease(text):
    parts = [part.split('\n') for part in text.split('/')]  
    
    global country
    global disease
    country = parts[0][0]
    disease = parts[1][0]
    
    return country, disease

# call the model to generate
def interact_summarization(n:str, trans:str, inter: str, assess:str, prompt: str, article: str) -> List[Tuple[str, str]]:
    # find out "country" and "disease"
    problem="""
    Please identify the main countries mentioned in the title of the article or the countries to which this region belongs, as well as the primary diseases mentioned.
    Please output in the format "Country/Disease".
    """
    input = f"{article}\n\n{problem}"
    country_disease = model.generate_content(
        input,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    country, disease = extract_country_disease(country_disease.text)
    #print(country, disease)

    # estimate "diagnostic method"
    problem=f"""
    Please mark the diagnostic method for {disease}, where "Clinical syndrome is diagnostic" represents a low score, "A simple laboratory test is diagnostic" is a intermediate score, and "Advanced or prolonged investigation is required for confirmatory diagnosis" represents a high score on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
    """
    diagnostic = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(diagnostic.text)

    # estimate "pathogen type"
    problem=f"""
    Please mark the pathogen type of {disease} as "Others," "Bacterial," or "Viral," with "Others" being a low score and "Viral" being a high score, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
    """
    pathogen = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(pathogen.text)

    # estimate "reservoir type"
    problem=f"""
    Please mark the reservoir type of {disease} as "Animal," "Environmental," or "Human," with "Animal" being a low score and "Human" being a high score, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
    """
    reservoir = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(reservoir.text)

    # estimate "basic reproductive number"
    problem=f"""Please mark the basic reproductive number of {disease} as "less than one," "one to two," or "greater than two," with "less than one" receiving a lower numerical score and "greater than two" receiving a higher numerical score, on a scale of 1 to 10 based on your own judgement.
    """
    reproductive = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(reproductive.text)

    # estimate "mode of transmission"
    problem=f"""Please mark the mode of transmission of {disease} as "Vector-borne or other animal-borne," "Foodborne, waterborne, and direct contact," or "Airborne or droplet," with "Vector-borne or other animal-borne" being a low score and "Airborne or droplet" being a high score, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
    """
    transmission = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(transmission.text)

    # estimate "mortality rate"
    problem=f"""Please mark the mortality rate of {disease} on a scale of 1 to 10 based on your own knowledge, with 1 being the lowest and 10 being the highest.
    """
    mortality = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(mortality.text)

    # estimate "incubation period"
    problem=f"""Please mark the incubation period of {disease} on a scale of 1 to 10 based on your own knowledge, with 1 being the shortest and 10 being the longest.
    """
    incubation = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(incubation.text)

    # estimate "GDP"
    problem=f"""Please indicate the GDP of {country} on a scale of 1 to 10, with 1 representing the wealthiest and 10 representing the poorest.
    """
    GDP = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(GDP.text)

    # estimate "population density"
    problem=f"""Please indicate the population density of {country} on a scale of 1 to 10, with 1 representing the sparsest and 10 representing the most crowded.
    """
    density = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(density.text)

    # estimate "government stability"
    problem=f"""Please indicate the level of peace and stability of {country} on a scale of 1 to 10, with 1 representing the most peaceful and 10 representing the most turbulent.
    """
    stability = model.generate_content(
        problem,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(stability.text)

    # estimate "level of exchange"
    input = f"{inter.format(country=country)}"
    interaction = model.generate_content(
        input,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
            ]
    )
    #print(interaction.text)

    global eleven
    eleven = f"""
1. Diagnostic method for {disease}: {diagnostic.text}
2. Pathogen type of {disease}: {pathogen.text}
3. Reservoir type of {disease}: {reservoir.text}
4. Basic reproductive number of {disease}: {reproductive.text}
5. Mode of transmission of {disease}: {transmission.text}
6. Mortality rate of {disease}: {mortality.text}
7. Incubation period of {disease}: {incubation.text}
8. GDP of {country}: {GDP.text}
9. Population density of {country}: {density.text}
10. Level of peace and stability of {country}: {stability.text}
11. Level of exchange with Taiwan of {country}: {interaction.text}
"""
    print(eleven)
    
    # generate the summary
    input = f"{prompt}\n{article}"
    response = model.generate_content(
        input,
        generation_config=genai.types.GenerationConfig(temperature=n),
        safety_settings=[
          {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
          {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
          {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
          {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
          ]
    )

    # generate the criteria
    input = f"{assess.format(disease=disease)}"
    assessRISK = model.generate_content(
        input,
        generation_config=genai.types.GenerationConfig(temperature=0),
        safety_settings=[
          {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
          {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
          {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
          {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
          ]
    )

    # translate the article into chinese
    total_score = int(diagnostic.text)+int(pathogen.text)+int(reservoir.text)+int(reproductive.text)+int(transmission.text)+int(mortality.text)+int(incubation.text)+int(GDP.text)+int(density.text)+int(stability.text)+int(interaction.text)
    assessment=response.text+"\n"+assessRISK+"\n\nRisk Score: "+str(total_score)+"/110"
    input = f"{trans}\n\n{assessment}"
    trans_article = model.generate_content(
      input,
      generation_config=genai.types.GenerationConfig(temperature=0)
    )

    return [(assessment, trans_article.text)]

def result_assessment() -> List[Tuple[str]]:
    global disease
    global country
    global eleven

    return [(eleven)]

# copy chatbox content
def copy_chatbox_content(chatbox_content):
    pyperclip.copy(chatbox_content[-1][-1])
    print("Chatbox content copied:", chatbox_content[-1][-1])

def main():

    with gr.Blocks() as demo:
        with gr.Column():
            gr.Markdown("# API key")
            api_textbox = gr.Textbox(label="API", placeholder="請輸入gemini的API key", type="password", interactive=True, value="")

        with gr.Column():
            gr.Markdown("# 疫情分析\n輸入一整篇新聞來製作摘要（不用刪去廣告沒關係）")
            prompt_textbox = gr.Textbox(label="Prompt", value=eval_prompt, visible=False)
            inter_textbox = gr.Textbox(label="Interaction", value=interact_risk, visible=False)
            assess_textbox = gr.Textbox(label="Assessment", value=assess_prompt, visible=False)
            trans_textbox = gr.Textbox(label="Translation", value=trans_prompt, visible=False)
            article_textbox = gr.Textbox(label="Article", interactive=True, placeholder="請在此輸入文章", value="")
            temperature_slider = gr.Slider(0.0, 1.0, 0.0, step = 0.1, label="Temperature")

        with gr.Row():
            sent_button = gr.Button(value="Send")
            clear_button = gr.Button(value="Clear")

        with gr.Column():
            chatbot = gr.Chatbot()
        with gr.Row():
            assess_button = gr.Button(value="Assess")
            copy_button = gr.Button(value="Copy")
        with gr.Column():
            result = gr.Chatbot()


        api_textbox.change(input_API, inputs=[api_textbox])
        sent_button.click(interact_summarization, inputs=[temperature_slider, trans_textbox, inter_textbox, assess_textbox, prompt_textbox, article_textbox], outputs=[chatbot])
        clear_button.click(clear, outputs=[article_textbox])
        assess_button.click(result_assessment, outputs=[result])
        copy_button.click(copy_chatbox_content, inputs=[chatbot])

    demo.launch(debug=True)

if __name__=='__main__':
    main()