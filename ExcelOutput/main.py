import openpyxl

from API import input_API
from Summary import Report
# from Scores import Assess

def main(text):
    api = "替換成自己的api key"
    model = input_API(api)
    Report(model, text)

if __name__=='__main__':
    text = input()
    main(text)