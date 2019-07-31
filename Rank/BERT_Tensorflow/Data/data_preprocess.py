import os
import numpy as np

curPath = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(curPath, "../../Dataset/enron1")
ham_dir = os.path.join(data_dir,"ham")
spam_dir = os.path.join(data_dir,"spam")

def load_file(dirpath,label):
    path_list = os.listdir(dirpath)
    data_set = []
    for path in path_list:
        filename = os.path.join(dirpath, path)
        with open(filename,"r",encoding = "utf-8",errors="ignore") as file:
            text = label+","
            for line in file:
                text += line.strip("\n")
            data_set.append(text)
    return data_set

def write_file(filename, data):
    length = len(data)
    with open(filename,"w",encoding="utf-8") as file:
        for i in range(length):
            file.write(str(data[i])+"\n")
        file.close()

if __name__ == '__main__':
    ham_set = load_file(ham_dir,"1")
    spam_set = load_file(spam_dir,"0")
    data = np.array(ham_set + spam_set)
    np.random.shuffle(data)
    msk = np.random.rand(len(data)) < 0.8
    train_data = data[msk]
    test_data = data[~msk]

    write_file("train.tsv",train_data)
    write_file("test.tsv", test_data)

