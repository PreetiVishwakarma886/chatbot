import json
import pickle
import random
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

lemmatizer = WordNetLemmatizer()

# Load intents
with open('intents.json') as file:
    data = json.load(file)

texts = []
labels = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        texts.append(pattern.lower())
        labels.append(intent['tag'])

# Vectorize text
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

# Train AI Model
model = MultinomialNB()
model.fit(X, labels)

# Save model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("✅ AI Model Trained Successfully!")