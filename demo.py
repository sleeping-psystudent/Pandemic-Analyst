import gradio as gr
import google.generativeai as genai
from typing import List, Tuple
import pyperclip
import re

GOOGLE_API_KEY = ""
model = None

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

"""
# clear the conversation
def reset() -> List:
    return []
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

# call the model to generate
def interact_summarization(trans:str, inter: str, prompt: str, article: str) -> List[Tuple[str, str]]:

    # estimate "交流程度"
    input = f"{article}\n\n{inter}"
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

    # generate the summary
    input = f"Level of exchange with Taiwan of <country>: {interaction.text}\n\n{prompt}\n{article}"
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

    # translate the article into chinese
    assessment=response.text+"\nRisk Score: "+str(extract(response.text))+"/110"
    input = f"{trans}\n\n{assessment}"
    trans_article = model.generate_content(
      input,
      generation_config=genai.types.GenerationConfig(temperature=0)
    )

    return [(assessment, trans_article.text)]

def result_assessment(article:str, assess:str, summary:str) -> List[Tuple[str, str]]:
    # assess the situation by sum up the scores
    input = f"{article}\n\n{assess}\n\n{summary[0][0]}"
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

    # translate
    input = f"請將下面文章翻譯成通順的臺灣繁體中文\n\n{assessRISK.text}"
    trans_article = model.generate_content(
      input,
      generation_config=genai.types.GenerationConfig(temperature=0)
    )

    return [(assessRISK.text, trans_article.text)]

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

        with gr.Row():
            sent_button = gr.Button(value="Send")
            # reset_button = gr.Button(value="Reset")

        with gr.Column():
            chatbot = gr.Chatbot()
        with gr.Row():
            assess_button = gr.Button(value="Assess")
            copy_button = gr.Button(value="Copy")
        with gr.Column():
            result = gr.Chatbot()


        api_textbox.change(input_API, inputs=[api_textbox])
        sent_button.click(interact_summarization, inputs=[trans_textbox, inter_textbox, prompt_textbox, article_textbox], outputs=[chatbot])
        # reset_button.click(reset, outputs=[chatbot])
        assess_button.click(result_assessment, inputs=[article_textbox, assess_textbox, chatbot], outputs=[result])
        copy_button.click(copy_chatbox_content, inputs=[chatbot])

    demo.launch(debug=True)

if __name__=='__main__':
    main()