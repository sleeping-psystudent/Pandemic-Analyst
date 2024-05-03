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
total_score = 0
trans_criteria = ""
situation = 0

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
    global situation
    situation = 0
    return None

# extract the numbers
def extract(text):
    numbers = re.findall(r'\d+', text)
    return numbers[0]


# extract country and disease
def extract_country_disease(text):
    parts = [part.split('\n') for part in text.split('/')]  
    
    global country
    global disease
    country = parts[0][0]
    disease = parts[1][0]
    
    return country, disease

# call the model to generate
def interact_summarization(trans:str, inter:str, assess:str, prompt: str, article: str) -> List[Tuple[str, str]]:
    if situation==0:
        # call assessment
        result_assessment(inter, article)
    
    # generate the summary
    input = f"{prompt}\n{article}"
    response = model.generate_content(
        input,
        generation_config=genai.types.GenerationConfig(temperature=0),
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
    assessment=response.text+"\n\n"+assessRISK.text+"\n\nRisk Score: "+str(total_score)+"/110"
    input = f"{trans}\n\n{assessment}"
    trans_article = model.generate_content(
      input,
      generation_config=genai.types.GenerationConfig(temperature=0)
    )

    return [(assessment, trans_article.text)]

def result_assessment(inter:str, article: str) -> List[Tuple[str, str]]:
    global eleven
    global total_score
    global trans_criteria
    global situation

    if situation == 0:
        # load model
        global model
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

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
        # problem=f"""
        # Please mark the diagnostic method for {disease}, where "Clinical syndrome is diagnostic" represents a low score, "A simple laboratory test is diagnostic" is a intermediate score, and "Advanced or prolonged investigation is required for confirmatory diagnosis" represents a high score on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
        # """
        # problem=f"""
        # Please mark the diagnostic method for {disease} on a scale of 1 to 10 based on your own knowledge. Please provide the numerical score only.
        # """
        problem=f"""You are now an epidemiologist and public health expert. Please rate the diagnostic difficulty of {disease} based on your judgement. "Clinical syndrome is diagnostic" corresponds to 1-3 points , "A simple laboratory test is diagnostic" corresponds to 4-6 points, and "Advanced or prolonged investigation is required for confirmatory diagnosis" corresponds to 7-9 points on a scale of 1 to 10. Please provide the numerical score only.
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
        # problem=f"""
        # Please mark the pathogen type of {disease} as "Others," "Bacterial," or "Viral," with "Others" being a low score and "Viral" being a high score, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
        # """
        # problem=f"""
        # Please mark the pathogen type of {disease} on a scale of 1 to 10 based on your own knowledge. Please provide the numerical score only.
        # """
        problem=f"""You are now an epidemiologist and public health expert. Please rate the severity of the pathogen type of {disease} as "Others," "Bacterial," or "Viral," with "Others" receiving 1-3 points, "Bacterial" receiving 4-6 points, and "Viral" receiving 7-9 points, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
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
        # problem=f"""
        # Please mark the reservoir type of {disease} as "Animal," "Environmental," or "Human," with "Animal" being a low score and "Human" being a high score, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
        # """
        # problem=f"""
        # Please mark the reservoir type of {disease} on a scale of 1 to 10 based on your own knowledge. Please provide the numerical score only.
        # """
        problem=f"""You are now an epidemiologist and public health expert. Please rate the intimacy of the host with humans for {disease}, with "Animal" being 1-3 points, "Environmental" being 4-6 points, and "Human" being 7-9 points, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
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
        # problem=f"""Please mark the basic reproductive number of {disease} as "less than one," "one to two," or "greater than two," with "less than one" receiving a lower numerical score and "greater than two" receiving a higher numerical score, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
        # """
        # problem=f"""Please mark the basic reproductive number of {disease}on a scale of 1 to 10 based on your own knowledge. Please provide the numerical score only.
        # """
        problem=f"""You are now an epidemiologist and public health expert. Please rate the infectiousness of {disease} based on your judgement, marking the basic reproductive number of {disease} as "less than one," "one to two," or "greater than two," with "less than one" receiving 1-3 points and "greater than two" receiving 7-9 points, on a scale of 1 to 10. Please provide the numerical score only.
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
        # problem=f"""Please mark the mode of transmission of {disease} as "Vector-borne or other animal-borne," "Foodborne, waterborne, and direct contact," or "Airborne or droplet," with "Vector-borne or other animal-borne" being a low score and "Airborne or droplet" being a high score, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
        # """
        # problem=f"""Please mark the mode of transmission of {disease} on a scale of 1 to 10 based on your own knowledge. Please provide the numerical score only.
        # """
        problem=f"""You are now an epidemiologist and public health expert. Please mark the mode of transmission of {disease} as "Vector-borne or other animal-borne," "Foodborne, waterborne, and direct contact," or "Airborne or droplet," and rate the ease of transmission, with "Vector-borne or other animal-borne" receiving 1-3 points and "Airborne or droplet" receiving 7-9 points, on a scale of 1 to 10 based on your own judgement. Please provide the numerical score only.
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
        problem=f"""You are now an epidemiologist and public health expert. Please mark the mortality rate of {disease} in humans on a scale of 1 to 10 based on your own knowledge, with 1 being the lowest and 10 being 100%.
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
        problem=f"""You are now an epidemiologist and public health expert. Please mark the incubation period of {disease} in humans on a scale of 1 to 10 based on your own knowledge, with 1 being the hours and 10 being years.
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

        eleven = f"""
    1. Diagnostic method for {disease}: {extract(diagnostic.text)}
    2. Pathogen type of {disease}: {extract(pathogen.text)}
    3. Reservoir type of {disease}: {extract(reservoir.text)}
    4. Basic reproductive number of {disease}: {extract(reproductive.text)}
    5. Mode of transmission of {disease}: {extract(transmission.text)}
    6. Mortality rate of {disease}: {extract(mortality.text)}
    7. Incubation period of {disease}: {extract(incubation.text)}
    8. GDP of {country}: {extract(GDP.text)}
    9. Population density of {country}: {extract(density.text)}
    10. Level of peace and stability of {country}: {extract(stability.text)}
    11. Level of exchange with Taiwan of {country}: {extract(interaction.text)}
    """
        total_score = int(extract(diagnostic.text))+int(extract(pathogen.text))+int(extract(reservoir.text))+int(extract(reproductive.text))+int(extract(transmission.text))+int(extract(mortality.text))+int(extract(incubation.text))+int(extract(GDP.text))+int(extract(density.text))+int(extract(stability.text))+int(extract(interaction.text))

        # translation
        trans="""
    請將下面翻譯成通順的臺灣繁體中文，
    範例如下，請參考表格畫法將評估標準內容以表格呈現。
    # 評估標準
    | 評估項目 | 評分 |
    |---|---|
    | 肉毒桿菌傳播率 | 1 |
    | 肉毒桿菌死亡率 | 3 |
    | 肉毒桿菌潛伏期 | 7 |
    | 俄羅斯 GDP | 1 |
    | 伊爾庫茨克人口密度 | 3 |
    | 俄羅斯政府穩定性 | 9 |
    | 俄羅斯與台灣的交流程度 | 4 |
    """
        input = f"{trans}\n\n{eleven}"
        trans_criteria = model.generate_content(
        input,
        generation_config=genai.types.GenerationConfig(temperature=0)
        )

        situation = 1
    else:
        situation = 0
    return [(eleven, trans_criteria.text)]

# copy chatbox content
def copy_chatbox_content(chatbox_content, result_content):
    pyperclip.copy(chatbox_content[-1][-1]+"\n"+result_content[-1][-1])

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
            clear_button = gr.Button(value="Clear")
        with gr.Row():
            sent_button = gr.Button(value="Send")
            assess_button = gr.Button(value="Assess")
        with gr.Row():
            chatbot = gr.Chatbot()
            result = gr.Chatbot()
        with gr.Row():
            copy_button = gr.Button(value="Copy")


        api_textbox.change(input_API, inputs=[api_textbox])
        sent_button.click(interact_summarization, inputs=[trans_textbox, inter_textbox, assess_textbox, prompt_textbox, article_textbox], outputs=[chatbot])
        clear_button.click(clear, outputs=[article_textbox])
        assess_button.click(result_assessment, inputs=[inter_textbox, article_textbox], outputs=[result])
        copy_button.click(copy_chatbox_content, inputs=[chatbot, result])

    demo.launch(debug=True)

if __name__=='__main__':
    main()