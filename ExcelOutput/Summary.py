import google.generativeai as genai
import time
from Scores import extract_country_disease

# load prompt
## summarize the article
with open("summarize.txt", "r") as file:
    summa_prompt = file.read()
## analyze the disease
with open("evaluate.txt", "r") as file:
    eval_prompt = file.read()
## translate en to zh
with open("translate.txt", "r") as file:
    trans_prompt = file.read()

# === Summary Main === #

def Report(model, article):
    # get disease and country
    country, disease = extract_country_disease(model, article)

    # generate the summary
    input = f"{summa_prompt}\n{article}"
    while(True):
        try:
            summa = model.generate_content(
                input,
                generation_config=genai.types.GenerationConfig(temperature=0),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
                    {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
                    ]
            )
            break
        except:
            time.sleep(5)
    

    # generate the criteria
    input = f"{eval_prompt.format(disease=disease)}"
    while(True):
        try:
            eval = model.generate_content(
                input,
                generation_config=genai.types.GenerationConfig(temperature=0),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_NONE",},
                    {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_NONE",},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE",},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE",},
                    ]
            )
            break
        except:
            time.sleep(5)

    # translate the article into chinese
    input = f"{trans_prompt}\n\n{summa.text}\n{eval.text}"
    while(True):
        try:
            trans_report = model.generate_content(
            input,
            generation_config=genai.types.GenerationConfig(temperature=0)
            )
            break
        except:
            time.sleep(5)

    return trans_report.text