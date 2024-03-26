import gradio as gr
import google.generativeai as genai
from typing import List, Tuple
import pyperclip

GOOGLE_API_KEY = ""
model = None

# load prompt
with open("translation.txt", "r") as file:
    trans_prompt = file.read()
with open("interaction.txt", "r") as file:
    interact_risk = file.read()
with open("prompt.txt", "r") as file:
    text_prompt = file.read()


# update global api
def input_API(api):
    global GOOGLE_API_KEY
    global model

    GOOGLE_API_KEY = api
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

# clear the conversation
def reset() -> List:
    return []

# call the model to generate
def interact_summarization(trans:str, inter: str, prompt: str, article: str) -> List[Tuple[str, str]]:
    # translate the article into chinese
    input = f"{trans}\n{article}"
    trans_article = model.generate_content(
      input,
      generation_config=genai.types.GenerationConfig(temperature=0)
    )

    # estimate "交流程度"
    input = f"{trans_article}\n{inter}"
    interaction = model.generate_content(
      input,
      generation_config=genai.types.GenerationConfig(temperature=0)
    )
    print(interaction.text)

    # generate the summary
    input = f"與臺灣交流程度\n{interaction.text}\n\n{prompt}\n{trans_article.text}"
    response = model.generate_content(
      input,
      generation_config=genai.types.GenerationConfig(temperature=0)
    )

    return [(trans_article.text, response.text)]

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
            prompt_textbox = gr.Textbox(label="Prompt", value=text_prompt, visible=False)
            inter_textbox = gr.Textbox(label="Interaction", value=interact_risk, visible=False)
            trans_textbox = gr.Textbox(label="Translation", value=trans_prompt, visible=False)
            article_textbox = gr.Textbox(label="Article", interactive=True, placeholder="請在此輸入文章", value="")

        with gr.Row():
            sent_button = gr.Button(value="Send")
            reset_button = gr.Button(value="Reset")

        with gr.Column():
            chatbot = gr.Chatbot()
        with gr.Row():
            copy_button = gr.Button(value="Copy")


        api_textbox.change(input_API, inputs=[api_textbox])
        sent_button.click(interact_summarization, inputs=[trans_textbox, inter_textbox, prompt_textbox, article_textbox], outputs=[chatbot])
        reset_button.click(reset, outputs=[chatbot])
        copy_button.click(copy_chatbox_content, inputs=[chatbot])

    demo.launch(debug=True)

if __name__=='__main__':
    main()
