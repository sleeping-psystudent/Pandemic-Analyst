import os
import gradio as gr

from API import input_API
from Summary import Report
from Scores import Assess
from Assessment import Train, Analyze
from ExcelExport import write_to_excel

def execute(text: str, num: None):
    api = os.getenv("GOOGLE_API_KEY")
    model = input_API(api)

    summary = Report(model, text)
    title, disease_items, country_items = Assess(model, text)
    if num == 0:
        scores = [disease_items["diagnostic"], disease_items["pathogen"], disease_items["reservoir"], disease_items["reproductive"], disease_items["transmission"], disease_items["mortality"], disease_items["therapy"], disease_items["vaccine"], country_items["GDP"], country_items["density"], country_items["stability"]]
        risk = Analyze(scores)
        data = [title, summary, risk, disease_items["diagnostic"], disease_items["pathogen"], disease_items["reservoir"], disease_items["reproductive"], disease_items["transmission"], disease_items["mortality"], disease_items["therapy"], disease_items["vaccine"], country_items["GDP"], country_items["density"], country_items["stability"]]
        path = "Data.xlsx"
        write_to_excel(path, data)
        return title+"\n"+risk+"\n"+summary
    else:
        data = [title, summary, num, disease_items["diagnostic"], disease_items["pathogen"], disease_items["reservoir"], disease_items["reproductive"], disease_items["transmission"], disease_items["mortality"], disease_items["therapy"], disease_items["vaccine"], country_items["GDP"], country_items["density"], country_items["stability"]]
        path = "Report.xlsx"
        write_to_excel(path, data)
        # update model
        Train()
        return title+"\n"+num+"\n"+summary

def clear():
    return "", ""

# ====================================================== #

def main():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                input_textbox = gr.Textbox(label="Input Text", placeholder="輸入文字")
                priority_slider = gr.Slider(
                    minimum=1,
                    maximum=4,
                    step=1,
                    label="風險評估\nWatchlist = 1, Low = 2, Medium = 3, High = 4",
                    value=0
                )
                with gr.Row():
                    submit_button = gr.Button("Update")
                    analyze_button = gr.Button("Analyze")
                    clear_button = gr.Button("Clear")
            output_textbox = gr.Textbox(label="評估結果", interactive=False)
                        
        # Hidden slider for Analyze button
        hidden_slider = gr.Slider(
                minimum=0,
                maximum=0,
                step=1,
                visible=False,
                value=0
            )

        submit_button.click(execute, inputs=[input_textbox, priority_slider], outputs=output_textbox)
        analyze_button.click(execute, inputs=[input_textbox, hidden_slider], outputs=output_textbox)
        clear_button.click(clear, inputs=None, outputs=[input_textbox, output_textbox])

    demo.launch(debug=True)

if __name__=='__main__':
    main()