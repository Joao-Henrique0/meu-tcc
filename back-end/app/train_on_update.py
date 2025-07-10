import json
import os
import time
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Caminhos dos arquivos
INTENTS_PATH = 'app/nlp/intents.json'
MODEL_PATH = 'app/nlp/chatbot_model.h5'
TOKENIZER_PATH = 'app/nlp/tokenizer.pkl'
LABEL_ENCODER_PATH = 'app/nlp/label_encoder.pkl'

# Função para treinar o modelo
def train_model():
    with open(INTENTS_PATH) as file:
        data = json.load(file)

    sentences = []
    labels = []
    classes = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            sentences.append(pattern)
            labels.append(intent['intent'])

    tokenizer = Tokenizer(num_words=5000, oov_token="<OOV>")
    tokenizer.fit_on_texts(sentences)
    sequences = tokenizer.texts_to_sequences(sentences)
    padded_sequences = pad_sequences(sequences, truncating='post', padding='post', maxlen=20)

    lbl_encoder = LabelEncoder()
    lbl_encoder.fit(labels)
    labels_encoded = lbl_encoder.transform(labels)

    model = Sequential()
    model.add(Embedding(input_dim=2000, output_dim=16, input_length=20))
    model.add(GlobalAveragePooling1D())
    model.add(Dense(16, activation='relu'))
    model.add(Dense(len(set(labels)), activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
    model.fit(padded_sequences, np.array(labels_encoded), epochs=500)

    # Salvar o modelo e os objetos
    model.save(MODEL_PATH)
    pickle.dump(tokenizer, open(TOKENIZER_PATH, 'wb'))
    pickle.dump(lbl_encoder, open(LABEL_ENCODER_PATH, 'wb'))
    print("✅ Modelo atualizado com sucesso!")

# Função para monitorar o intents.json
def monitor_intents(interval=10):
    last_modified = None
    while True:
        if os.path.exists(INTENTS_PATH):
            current_modified = os.path.getmtime(INTENTS_PATH)
            if last_modified is None:
                last_modified = current_modified

            if current_modified != last_modified:
                print("🔄 Alteração detectada no intents.json. Re-treinando o modelo...")
                try:
                    train_model()
                except Exception as e:
                    print(f"❌ Erro ao treinar o modelo: {e}")
                last_modified = current_modified
        time.sleep(interval)

if __name__ == "__main__":
    print("👀 Monitorando alterações no intents.json...")
    monitor_intents()
