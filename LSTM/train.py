import pickle
from keras.layers.core import Activation, Dense, SpatialDropout1D
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.preprocessing import sequence
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import jieba
import numpy as np
import pandas as pd
import csv

with open('model/word_dict.pickle', 'rb') as handle:
    word2index = pickle.load(handle)

### prepare data
MAX_FEATURES = 40000 # 最大詞頻數
MAX_SENTENCE_LENGTH = 80
num_recs = 0  # 樣本數

csv_file = open("data/2.csv", encoding="utf-8")
lines = csv.reader(csv_file)
for line in lines:
    num_recs += 1

# 初始化句子數组和label數组
X = np.empty(num_recs,dtype=list)
y = np.zeros(num_recs)
i=0

csv_file = open("data/2.csv", encoding="utf-8")
lines = csv.reader(csv_file)
for line in lines:
    label = line[0]
    sentence = line[1].replace(' ', '')
    words = jieba.cut(sentence)
    seqs = []
    for word in words:
        if word in word2index:
            seqs.append(word2index[word])
        else:
            seqs.append(word2index["UNK"])
    X[i] = seqs
    y[i] = int(label)
    i += 1

X = sequence.pad_sequences(X, maxlen=MAX_SENTENCE_LENGTH)
# 對label one-hot encoding
y1 = pd.get_dummies(y).values
print(X.shape)
print(y1.shape)

Xtrain, Xtest, ytrain, ytest = train_test_split(X, y1, test_size=0.2, random_state=42)
# network
EMBEDDING_SIZE = 256 # wordvector维度
HIDDEN_LAYER_SIZE = 128
BATCH_SIZE = 16
NUM_EPOCHS = 5

model = Sequential()
# 構建詞向量
model.add(Embedding(MAX_FEATURES, EMBEDDING_SIZE,input_length=MAX_SENTENCE_LENGTH))
model.add(SpatialDropout1D(0.2))
# LSTM層
model.add(LSTM(HIDDEN_LAYER_SIZE, dropout=0.2, recurrent_dropout=0.2))
# 輸出層包含3類
model.add(Dense(3, activation="softmax"))
model.add(Activation('softmax'))
model.compile(loss="categorical_crossentropy", optimizer="adam",metrics=["accuracy"])

model.fit(Xtrain, ytrain, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,validation_data=(Xtest, ytest))

y_pred = model.predict(Xtest)
y_pred = y_pred.argmax(axis=1)
ytest = ytest.argmax(axis=1)

print('accuracy %s' % accuracy_score(y_pred, ytest))
target_names = ['1 or 2', '3', '4 or 5']
print(classification_report(ytest, y_pred, target_names=target_names))

model.save('model/my_model.h5')