import gradio as gr

from API import input_API
from Summary import Report
from Scores import Assess
from ExcelExport import write_to_excel

def execute(text):
    # api = "Your api key"
    model = input_API(api)

    summary = Report(model, text)
    title, disease_items, country_items = Assess(model, text)
    # calculate the risk
    data = [title, summary, disease_items["diagnostic"], disease_items["pathogen"], disease_items["reservoir"], disease_items["reproductive"], disease_items["transmission"], disease_items["mortality"], disease_items["therapy"], disease_items["vaccine"], country_items["GDP"], country_items["density"], country_items["stability"]]
    # data = [title, risk, summary]

    path = "Data.xlsx"
    write_to_excel(path, data)

    return title+"\n"+summary

def clear():
    return "", ""

# ====================================================== #

def main():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                input_textbox = gr.Textbox(label="Input Text", placeholder="輸入文字")
                submit_button = gr.Button("Submit")
            with gr.Column():
                output_textbox = gr.Textbox(label="Result", interactive=False)
                clear_button = gr.Button("Clear")

        submit_button.click(execute, inputs=input_textbox, outputs=output_textbox)
        clear_button.click(clear, inputs=None, outputs=[input_textbox, output_textbox])

    demo.launch(debug=True)

if __name__=='__main__':
    main()