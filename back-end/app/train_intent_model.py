import json
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

# Carregar dataset
with open('app/nlp/intents.json') as file:
    data = json.load(file)

sentences = []
labels = []
classes = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        sentences.append(pattern)
        labels.append(intent['intent'])

# Tokenizar frases
tokenizer = Tokenizer(num_words=2000, oov_token="<OOV>")
tokenizer.fit_on_texts(sentences)
word_index = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(sentences)
padded_sequences = pad_sequences(sequences, truncating='post', padding='post', maxlen=20)

# Codificar intenções
lbl_encoder = LabelEncoder()
lbl_encoder.fit(labels)
labels_encoded = lbl_encoder.transform(labels)

# Construir modelo
model = Sequential()
model.add(Embedding(input_dim=2000, output_dim=16, input_length=20))
model.add(GlobalAveragePooling1D())
model.add(Dense(16, activation='relu'))
model.add(Dense(len(set(labels)), activation='softmax'))

# Compilar
model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

# Treinar
model.fit(padded_sequences, np.array(labels_encoded), epochs=200)

# Salvar modelo e codificadores
model.save('app/nlp/chatbot_model.h5')
pickle.dump(tokenizer, open('app/nlp/tokenizer.pkl', 'wb'))
pickle.dump(lbl_encoder, open('app/nlp/label_encoder.pkl', 'wb'))

print("Modelo treinado e salvo com sucesso!")
