import re
import pandas as pd # CSV file I/O (pd.read_csv)
from nltk.corpus import stopwords
import numpy as np
import sklearn
import fasttext

'''
fasttext_v2 is for uci-news-aggregator dataset, wihch is in csv format and classifies news to different categories.
'''
def get_words( headlines ):
    headlines_onlyletters = re.sub("[^a-zA-Z]", " ",headlines) #Remove everything other than letters
    words = headlines_onlyletters.lower().split() #Convert to lower case, split into individual words
    stops = set(stopwords.words("english"))  #Convert the stopwords to a set for improvised performance
    meaningful_words = [w for w in words if not w in stops]   #Removing stopwords
    return( " ".join( meaningful_words )) #Joining the words

news = pd.read_csv("uci-news-aggregator.csv") #Importing data from CSV
news = (news.loc[news['CATEGORY'].isin(['b','e'])]) #Retaining rows that belong to categories 'b' and 'e'
X_train, X_test, Y_train, Y_test = sklearn.model_selection.train_test_split(news["TITLE"], news["CATEGORY"], test_size = 0.2)
X_train = np.array(X_train)
X_test = np.array(X_test)
Y_train = np.array(Y_train)
Y_test = np.array(Y_test)
cleanHeadlines_train = [] #To append processed headlines
cleanHeadlines_test = [] #To append processed headlines
number_reviews_train = len(X_train) #Calculating the number of reviews
number_reviews_test = len(X_test) #Calculating the number of reviews

for i in range(0,number_reviews_train):
    cleanHeadline = get_words(X_train[i]) #Processing the data and getting words with no special characters, numbers or html tags
    cleanHeadlines_train.append( cleanHeadline )

for i in range(0, number_reviews_test):
    cleanHeadline = get_words(
        X_test[i])  # Processing the data and getting words with no special characters, numbers or html tags
    cleanHeadlines_test.append(cleanHeadline)

# print(cleanHeadlines_train[0:10])
# print(Y_test[0:10])
# print(Y_train[0:10])

f = open('train.txt', 'w')
for i in range(number_reviews_train):
    f.writelines([cleanHeadlines_train[i], ' '])
    f.writelines(['     '])
    f.writelines(['__label__'])
    f.writelines([Y_train[i]])
    f.writelines(['\n'])

f.close()

f = open('test.txt', 'w')
for i in range(number_reviews_test):
    f.writelines([cleanHeadlines_test[i], ' '])
    f.writelines(['     '])
    f.writelines(['__label__'])
    f.writelines([Y_test[i]])
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

total = 0.0
correct = 0.0
with open("test.txt") as fr:
    lines = fr.readlines()
for line in lines:
    labels_right.append(line.split("__label__")[1])
    texts.append(line.split("\n")[0])
    labels_predict.append(classifier.predict_proba(line)[0][0])
    total+=1
    # print(classifier.predict_proba([line[0:-16]])[0][0][0])
    # print(line[-2])
    # print(classifier.predict_proba([line[0:-16]])[0][0][0] == line[-2])
    if classifier.predict_proba([line[0:-16]])[0][0][0] == line[-2]:
        correct+=1
    # print(total)
    # print(correct)
print("correct rate = " + str(correct/total))
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