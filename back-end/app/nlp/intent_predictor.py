import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re

# Carregar o modelo treinado e os utilitários
model = load_model('app/nlp/chatbot_model.h5')
tokenizer = pickle.load(open('app/nlp/tokenizer.pkl', 'rb'))
lbl_encoder = pickle.load(open('app/nlp/label_encoder.pkl', 'rb'))


def preprocess_text(text):
    text = text.lower()  # Converter para minúsculas
    text = re.sub(r'[^\w\s]', '', text)  # Remover pontuações
    text = re.sub(r'\s+', ' ', text).strip()  # Remover espaços extras
    return text

# Função de previsão de intenção
def predict_intent(message):
    message = preprocess_text(message)  # Pré-processar a mensagem
    sequence = tokenizer.texts_to_sequences([message])
    padded = pad_sequences(sequence, truncating='post', padding='post', maxlen=20)
    predictions = model.predict(padded)
    confidence = np.max(predictions)
    intent_class = np.argmax(predictions)
    intent_label = lbl_encoder.inverse_transform([intent_class])[0]
    
    return intent_label, float(confidence)
