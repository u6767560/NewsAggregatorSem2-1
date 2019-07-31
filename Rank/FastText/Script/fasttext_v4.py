import random
import codecs
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import os
import fasttext
import json
import sklearn
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import numpy as np
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.metrics import auc
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import spacy
import pickle

pickle_root = '../../HDBSCAN/Output/text_300k.p'
nlp = spacy.load('en_core_web_lg')
headlines = pickle.load(open(pickle_root, "rb" ))
train_dir = '../Data/train.txt'
test_dir = '../Data/test.txt'
result_dir = '../Results'
model_dir = '../Output/kosmos3'
read_model_dir = '../Output/kosmos3.bin'

'''
load article, label and id, then seperate into train and test.
'''
def load_files(dataset):
    art_set = []
    label_set = []
    id_sequence = []
    train = []
    zeros = 0
    for i in range(len(dataset)):
        try:
            id_sequence.append(dataset[i][0][7:])
        except:
            id_sequence.append(i)
        article = dataset[i][1]
        label = dataset[i][2]

        if label == '1':
            if random.random() > 0.9:  # Divide the dataset into train and test sets
                train.append("test")
                art_set.append(article)
                label_set.append(label)
            else:
                train.append("train")
                art_set.append(article)
                label_set.append(label)

        elif label == '0' and random.random() > 0.1:
            if random.random() > 0.9:  # Divide the dataset into train and test sets
                train.append("test")
                art_set.append(article)
                label_set.append(label)
            else:
                train.append("train")
                art_set.append(article)
                label_set.append(label)
        if i > 299900:
            break
    # print("art 0", i, art_set[0])
    return art_set, label_set, id_sequence, train

'''
write train and test file according to fasttext model requirement
'''
def write_dataset(train_dir,test_dir,train,art_set, label_set):# write the labeled dataset into .txt files to be suitable for modelling
    s_div = []
    for i in art_set:
        stop_words = set(stopwords.words('english'))
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(i)
        filtered_sentence = [w for w in tokens if not w in stop_words]
        s_div.append(filtered_sentence)
    f = open(train_dir, 'w')
    for i in range(len(s_div)):
        if train[i] == "train":
            for j in range(len(s_div[i])):
                f.writelines([s_div[i][j],' '])
            f.writelines(['     '])
            f.writelines(['__label__'])
            f.writelines([label_set[i]])
            f.writelines(['\n'])
    f.close()
    f = open(test_dir, 'w')
    for i in range(len(s_div)):
        if train[i] == "test":
            for j in range(len(s_div[i])):
                f.writelines([s_div[i][j],' '])
            f.writelines(['     '])
            f.writelines(['__label__'])
            f.writelines([label_set[i]])
            f.writelines(['\n'])
    f.close()

'''
generate predict result to ideal format, and evaluate with AUC and confusion matrix.
'''
def generate_result(test_dir,classifier):# use fasttext to predict the mails into spam or ham
    labels_right = []
    texts = []
    labels_predict = []
    total = 0.0
    correct = 0.0
    not_zero = 0
    TN =0.0
    FP = 0.0
    FN = 0.0
    TP = 0.0
    spam_rate = {}# store the result into the dict spam_rate
    with open(test_dir) as fr:
        lines = fr.readlines()
    for line in lines:
        labels_right.append(line.split("__label__")[1])
        texts.append(line.split("\n")[0])
        labels_predict.append(classifier.predict_proba(line)[0][0])
        total+=1
        predict_value = 1 if classifier.predict_proba([line[0:-10]])[0][0][0] == '1' else 0
        if predict_value == 1:
            not_zero +=1
        real_value = 1 if line[-2:-1] == '1' else 0
        if predict_value == 1:
            spam_rate[int(total)] = [classifier.predict_proba([line[0:-10]])[0][0][1],predict_value,real_value]
        else:
            spam_rate[int(total)] = [round(1.0-float(classifier.predict_proba([line[0:-10]])[0][0][1]),6), predict_value, real_value]
        if predict_value == real_value:
            correct+=1
        if (predict_value == 0 and real_value == 0):
            TN+=1
        elif (predict_value == 1 and real_value ==0):
            FP+=1
        elif (predict_value == 0 and real_value == 1):
            FN+=1
        elif (predict_value == 1 and real_value == 1):
            TP+=1

    print("accuracy = ",correct/total)

    print('TN',TN,'FP',FP,'FN',FN,'TP',TP)
    print("not zero numbers:" + str(not_zero))
    result = []
    real = []
    predict = []
    score = []

    for key in spam_rate.keys():# print and write the return value
        #print(str(key) + "," + str(spam_rate[key][0])+ "," + 'predict',str(spam_rate[key][1]),'real',str(spam_rate[key][2]))
        result.append(str(key) + "," + str(spam_rate[key][0])+ "," + str(spam_rate[key][1]))
        real.append(spam_rate[key][2])
        predict.append((spam_rate[key][1]))
        score.append(spam_rate[key][0])
    lab = np.array(real)
    # print(lab)
    pre = np.array(predict)
    scores = np.array(score)
    fpr, tpr, thresholds = metrics.roc_curve(lab, scores, pos_label=1)

    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')

    from sklearn.metrics import auc
    AUC = auc(fpr, tpr)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 12.5)
    s = 'AUC is {n} .'
    plt.plot(fpr, tpr, marker='o')
    plt.title(s.format(n=AUC), fontsize=20, fontweight='bold')
    plt.savefig(result_dir+"/AUC_kosmos3.jpg")
    plt.show()

    print("Accuracy Score: %f\n" % metrics.accuracy_score(real, predict))
    labels = ['unimportant', 'important']
    print(classification_report(real, predict, target_names=labels, digits=6))
    image = confusion_matrix(real, predict)
    plot_confusion(image, labels=labels)
    plt.savefig(result_dir + "/Confusion Matrix_kosmos3.jpg")
    plt.show()

    return result

'''
plot confusion matrix
'''
def plot_confusion(cm, title='Confusion matrix', cmap=plt.cm.Reds, labels=[]):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45)
    plt.yticks(tick_marks, labels)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def main():
    art_set, label_set, id_sequence, train = load_files(headlines)
    write_dataset(train_dir,test_dir,train,art_set,label_set)
    classifier = fasttext.supervised(train_dir, model_dir, label_prefix="__label__", word_ngrams=1, bucket=10)
    classifier = fasttext.load_model(read_model_dir, label_prefix='__label__')
    result = classifier.test(test_dir)
    result = generate_result(test_dir, classifier)
    return result

main()

