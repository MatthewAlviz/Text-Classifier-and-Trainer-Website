#import library
import fastText
import pandas as pd
import re
from nltk.corpus import stopwords
from io import StringIO
import csv

#pre-process data
dataset = pd.read_csv('/home/osboxes/Desktop/ML PROJECT/Machine Learning Algorithms/FastText Algorithm/ML PROJECT.csv')
col = ['Knowledge Base', 'Short Description']
test1 = dataset[col]

#Store data to csv file
test1['Knowledge Base']=['__label__'+s.replace(' or ', '$').replace(', or ','$').replace(',','$').replace(' ','_').replace(',','__label__').replace('$$','$').replace('$',' __label__').replace('___','__') for s in test1['Knowledge Base']]
test1['Knowledge Base']
test1['Short Description']= test1['Short Description'].replace('\n',' ', regex=True).replace('\t',' ', regex=True)

REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower() # lowercase text
    text = REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text
    text = BAD_SYMBOLS_RE.sub('', text) # delete symbols which are in BAD_SYMBOLS_RE from text
    text = ' '.join(word for word in text.split() if word not in STOPWORDS) # delete stopwors from text
    return text

test1['Short Description'] = test1['Short Description'].apply(clean_text)

test1.to_csv('/home/osboxes/Desktop/ML PROJECT/Machine Learning Algorithms/FastText Algorithm/preprocessed.txt', index=False, sep=' ', header=False, escapechar=" ", quoting=csv.QUOTE_NONE)
