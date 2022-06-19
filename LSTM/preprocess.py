import collections
import pickle
import re
import jieba
import csv

def regex_filter(s_line):
    # 英文、數字，空格
    special_regex = re.compile(r"[a-zA-Z0-9\s]+")
    # 英文標點符號和特殊符號
    en_regex = re.compile(r"[.…{|}#$%&\'()*+,!-_./:~^;<=>?@★●，。]+")
    # 中文標點符號
    zn_regex = re.compile(r"[《》、，“”；～？！：（）【】]+")

    s_line = special_regex.sub(r"", s_line)
    s_line = en_regex.sub(r"", s_line)
    s_line = zn_regex.sub(r"", s_line)
    return s_line

# 加載停用詞
def stopwords_list(file_path):
    stopwords = [line.strip() for line in open(file_path, 'r', encoding='utf-8').readlines()]
    return stopwords

word_freqs = collections.Counter()  # 詞頻
stopword = stopwords_list("data/stopWords.txt")
max_len = 0
csv_file = open("data/2.csv", encoding="utf-8")
lines = csv.reader(csv_file)
for line in lines:
    label = line[0]
    sentence = line[1].replace(' ', '')
    
    sentence = regex_filter(sentence)
    words = jieba.cut(sentence)
    x = 0
    for word in words:
        if word not in stopword:
            word_freqs[word] += 1
            x += 1
            print(word)
    max_len = max(max_len, x)
print(max_len)
print('nb_words ', len(word_freqs))


MAX_FEATURES = 40000
vocab_size = min(MAX_FEATURES, len(word_freqs)) + 2
# 建構詞頻字典
word2index = {x[0]: i+2 for i, x in enumerate(word_freqs.most_common(MAX_FEATURES))}
word2index["PAD"] = 0
word2index["UNK"] = 1

with open('model/word_dict.pickle', 'wb') as handle:
    pickle.dump(word2index, handle, protocol=pickle.HIGHEST_PROTOCOL)