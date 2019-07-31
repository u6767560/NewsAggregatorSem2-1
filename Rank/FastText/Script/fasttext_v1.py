import pandas as pd
import random
import fasttext
import codecs
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

'''
fasttext_v1 is for 20news-18828 dataset, which classifies news to different categories.
'''

path = "20news-18828"
files0 = os.listdir(path)
s = []
type = []
train = []
print('hello')

# def load_data(path):
for i in files0:
    # print i
    # print(os.path.isdir(path + "/" + i))
    if os.path.isdir(path + "/" + i):
        # print(i)
        # print(used)
        small_path = path + "/" + i
        files = os.listdir(small_path)
        for file in files:
            if not os.path.isdir(file):
                f = open(small_path + "/" + file)
                iter_f = iter(f)
                str = ""
                for line in iter_f:
                    str = str + line
                s.append(str)
                type.append(i)
                if random.random() >0.9:
                    train.append("test")
                else:
                    train.append("train")
        print(len(s))

print(s[0])
print(type[0])
print(train[0])



# print(filtered_sentence)
s_div = []
for i in s:
    stop_words = set(stopwords.words('english'))
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(i)
    filtered_sentence = [w for w in tokens if not w in stop_words]
    s_div.append(filtered_sentence)
# print(s_div[0])

f = open('train.txt', 'w')
for i in range(len(s_div)):
    if train[i] == "train":
        for j in range(len(s_div[i])):
            f.writelines([s_div[i][j],' '])
        f.writelines(['     '])
        f.writelines(['__label__'])
        f.writelines([type[i]])
        f.writelines(['\n'])
f.close()

f = open('test.txt', 'w')
for i in range(len(s_div)):
    if train[i] == "test":
        for j in range(len(s_div[i])):
            f.writelines([s_div[i][j],' '])
        f.writelines(['     '])
        f.writelines(['__label__'])
        f.writelines([type[i]])
        f.writelines(['\n'])
f.close()

classifier = fasttext.supervised("train.txt","news_fasttext.model",label_prefix="__label__",word_ngrams=5, bucket=10)
classifier = fasttext.load_model('news_fasttext.model.bin', label_prefix='__label__')
result = classifier.test("test.txt")

print(result.precision)
print(result.recall)
print(result.nexamples)

labels_right = []
texts = []
labels_predict = []
with open("test.txt") as fr:
    lines = fr.readlines()
for line in lines:
    labels_right.append(line.split("__label__")[1])
    texts.append(line.split("\n")[0])
    labels_predict.append(classifier.predict(line)[0][0])
    # print labels_right
#     print texts
#     break

print(len(labels_predict))
print(len(labels_right))
# print labels_predict
text_labels = list(set(labels_right))
text_predict_labels = list(set(labels_predict))
print(text_predict_labels)
print(text_labels)
print(labels_predict[0:10])
print(labels_right[0:10])
#     print tokens
# load_data(path)