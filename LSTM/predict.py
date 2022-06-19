import pickle
import re
import jieba
import numpy as np
from keras.models import load_model
from keras.preprocessing import sequence

MAX_SENTENCE_LENGTH = 80
model = load_model('model/my_model.h5')
# preprocess
def regex_filter(s_line):
    # 英文、數字，以及空格
    special_regex = re.compile(r"[a-zA-Z0-9\s]+")
    # 英文標點符號和特殊符號
    en_regex = re.compile(r"[.…{|}#$%&\'()*+,!-_./:~^;<=>?@★●，。]+")
    # 中文標點符號
    zn_regex = re.compile(r"[《》、，“”；～？！：（）【】]+")

    s_line = special_regex.sub(r"", s_line)
    s_line = en_regex.sub(r"", s_line)
    s_line = zn_regex.sub(r"", s_line)
    return s_line

def predict(sentence):
    with open('model/word_dict.pickle', 'rb') as handle:
        word2index = pickle.load(handle)

    xx = np.empty(1, dtype=list)
    # 數據預處理
    sentence = regex_filter(sentence)
    words = jieba.cut(sentence)
    seq = []
    for word in words:
        if word in word2index:
            seq.append(word2index[word])
        else:
            seq.append(word2index['UNK'])
    xx[0] = seq
    xx = sequence.pad_sequences(xx, maxlen=MAX_SENTENCE_LENGTH)

    label2word = {0: '1 or 2', 1: '3', 2: '4 or 5'}
    for x in model.predict(xx):
        x = x.tolist()
        label = x.index(max(x[0], x[1], x[2]))
        print('{}'.format(label2word[label]))

#sentence = '請改善備份問題！每次加密備份需要5個小時以上（已使用wifi備份），導致手機運行及數據及電量十分消耗，猜想是語音訊息太多？？？ 請改善此問題，謝謝你們，辛苦了！！'
predict('請改善備份問題！每次加密備份需要5個小時以上（已使用wifi備份），導致手機運行及數據及電量十分消耗，猜想是語音訊息太多？？？ 請改善此問題，謝謝你們，辛苦了！！')
predict('快捷 安全可靠 方便容易使用')
predict('即使不更新也比微信好用多了。')
predict("安裝一半一直出現沒有網路的錯誤訊息無法完成。之後使用what's app發信息給朋友時卻在對方對話框中一直出現此人正在申請what's app budiness的訊息，每傳一條訊息就出現一大片這個英文，很佔版面，就算觧除安裝Business，問題還是存在。")