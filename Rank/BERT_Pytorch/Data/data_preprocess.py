import os
import json
import numpy as np
from sklearn.model_selection import train_test_split

curPath = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(curPath, "../../Dataset/News_10d")

def load_files(dirname):
    path_list = os.listdir(dirname)
    data_set = []
    for path in path_list:
        filename = os.path.join(dirname, path)
        with open(filename, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                ins = ""
                text = json.loads(line)
                content = text["art"]
                label = text["importance"]
                ins += label+",Article:"+content
                data_set.append(ins)
    return data_set

def write_file(filename, data):
    length = len(data)
    with open(filename,"w",encoding="utf-8") as file:
        for i in range(length):
            file.write(str(data[i])+"\n")
        file.close()

if __name__ == '__main__':
    dataset = load_files(data_dir)
    train, test = train_test_split(dataset, test_size=0.1)
    write_file("train.tsv",train)
    write_file("test.tsv", test)
