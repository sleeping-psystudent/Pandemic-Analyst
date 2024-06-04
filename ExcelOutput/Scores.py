import google.generativeai as genai
import time
import re

# extract the numbers
def extract_num(text):
    numbers = re.findall(r'\d+', text)
    return int(numbers[0])

# extract country and disease in the article
def extract_country_disease(model, article):
    # find out "country" and "disease"
    problem="""
    Please identify the main countries mentioned in the title of the article or the countries to which this region belongs, as well as the primary diseases mentioned.
    Please output in the format "Country/Disease".
    """
    input = f"{article}\n\n{problem}"
    while(True):
        try:
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
            break
        except:
            time.sleep(5)

    text = country_disease.text
    parts = [part.split('\n') for part in text.split('/')]  
    
    country = parts[0][0]
    disease = parts[1][0]
    
    return country, disease


def disease_items(model, disease):
    disease_scores = {}

    # estimate "diagnostic method"
    problem = f"""You are now an epidemiologist and public health expert. Please rate the diagnostic difficulty of {disease} based on your judgement. If "clinical syndrome is diagnostic", then it corresponds to 1 point . "A simple laboratory test is diagnostic" corresponds to 2 points, and "Advanced or prolonged investigation is required for confirmatory diagnosis" corresponds to 3 points. Please provide the numerical score only.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    disease_scores["diagnostic"] = extract_num(diagnostic.text)

    # estimate "pathogen type"
    problem=f"""You are now an epidemiologist and public health expert. Please rate the severity of the pathogen type of {disease} as "Others," "Bacterial," or "Viral," with "Others" receiving 1 point, "Bacterial" receiving 2 points, and "Viral" receiving 3 points based on your own judgement. Please provide the numerical score only.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5) 
    disease_scores["pathogen"] = extract_num(pathogen.text)

    # estimate "reservoir type"
    problem=f"""You are now an epidemiologist and public health expert. Please rate the intimacy of the host with humans for {disease}, with "Animal" being 1 point, "Environmental" being 2 points, and "Human" being 3 points based on your own judgement. Please provide the numerical score only.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    disease_scores["reservoir"] = extract_num(reservoir.text)

    # estimate "basic reproductive number"
    problem=f"""You are now an epidemiologist and public health expert. First, recall the basic reproductive number of {disease}, then rate the infectiousness of {disease} based on your judgement, marking the basic reproductive number of {disease} as "less than one," "one to two," or "greater than two," with "less than one" receiving 1 point, "one to two" receiving 2 points and "greater than two" receiving 3 points. Please provide the numerical score only.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    disease_scores["reproductive"] = extract_num(reproductive.text)

    # estimate "mode of transmission"
    problem=f"""You are now an epidemiologist and public health expert. Please mark the mode of transmission of {disease} as "Vector-borne or other animal-borne," "Foodborne, waterborne, and direct contact," or "Airborne or droplet," and rate the ease of transmission, with "Vector-borne or other animal-borne" receiving 1 point, "Foodborne, waterborne, and direct contact" receiving 2 points and "Airborne or droplet" receiving 3 points, based on your own judgement. Please provide the numerical score only.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    disease_scores["transmission"] = extract_num(transmission.text)

    # estimate "mortality rate"
    problem=f"What is the mortality rate of {disease}?"
    while(True):
        try:
            rate = model.generate_content(
                problem,
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
    problem=f"""The mortality rate of {disease} is {rate.text}. If the mortality rate is less than 1 percent, please score 1 point; if it is between 1 to 5 percent, please score 2 points; if it is greater than 5 percent, please score 3 points. Please provide the numerical score only.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    disease_scores["mortality"] = extract_num(mortality.text)

    # estimate "treatment availability"
    problem=f"""For {disease}, please mark 1 point if there is an effective therapy or drug available, or 3 points if not. Please provide the numerical score only.
    """
    while(True):
        try:
            therapy = model.generate_content(
                problem,
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
    disease_scores["therapy"] = extract_num(therapy.text)

    problem=f"""For {disease}, please mark 1 point if there is a vaccine available, or 3 points if not. Please provide the numerical score only.
    """
    while(True):
        try:
            vaccine = model.generate_content(
                problem,
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
    disease_scores["vaccine"] = extract_num(vaccine.text)

    return disease_scores

def country_items(model, country):
    country_scores = {}

    # estimate "GDP"
    problem=f"""Please indicate the GDP of {country} on a scale of 1 to 3, with 1 representing the wealthiest and 3 representing the poorest.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    country_scores["GDP"] = extract_num(GDP.text)

    # estimate "population density"
    problem=f"""Please indicate the population density of {country} on a scale of 1 to 3, with 1 representing the sparsest and 3 representing the most crowded.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    country_scores["density"] = extract_num(density.text)

    # estimate "government stability"
    problem=f"""Please indicate the level of peace and stability of {country} on a scale of 1 to 3, with 1 representing the most peaceful and 3 representing the most turbulent.
    """
    while(True):
        try:
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
            break
        except:
            time.sleep(5)
    country_scores["stability"] = extract_num(stability.text)

    return country_scores

# === Assess Main === #

def Assess(model, article):
        country, disease = extract_country_disease(model, article)
        return disease, country, disease_items(model, disease), country_items(model, country)