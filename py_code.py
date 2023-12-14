import pandas as pd
# import re
from flask import Flask, render_template, request
from fuzzywuzzy import fuzz
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load patent data
data_path = "C:\\templates\\Dronealexa.xlsx"
data = pd.read_excel(data_path)

def clean_title(title):
    return title.lower().strip()

def find_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def find_abstracts(keywords):
    abstracts = []
    phrase = " ".join(keywords)
    for i, row in data.iterrows():
        title = row["Title"].lower()
        abstract = row["Abstract"].lower()

        # Check if the entire phrase is present in the title or abstract
        if phrase.lower() in title or phrase.lower() in abstract or fuzz.ratio(phrase.lower(), title) > 80 or fuzz.ratio(phrase.lower(), abstract) > 80:
            entities_in_title = find_entities(title)
            entities_in_abstract = find_entities(abstract)
            abstracts.append({
                "Title": row["Title"],
                "Abstract": row["Abstract"],
                "Url": row.get("url", ""),
                "EntitiesInTitle": entities_in_title,
                "EntitiesInAbstract": entities_in_abstract
            })

    return abstracts

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        keywords = user_input.lower().split()
        abstracts = find_abstracts(keywords)
        return render_template('index.html', user_input=user_input, abstracts=abstracts)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
