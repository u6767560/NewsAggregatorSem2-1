**Fasttext introduction**

The 4 versions of fasttext are basically same for different data formats.

1. fasttext_v1 is for 20news-18828 dataset, which classifies news to different categories.

2. fasttext_v2 is for uci-news-aggregator dataset, wihch is in csv format and classifies news to different categories.

3. fasttext_v3 is for news_10d dataset, which is in txt format with json content. It classifies news into important/ unimportant according to HDBSCAN results.

4. fasttext_v4 is for kosmos3 dataset, which is pickle file for world news article. It classifies news into import/ unimportant according to HDBSCAN results.

**Dataset**

Datasets are not uploaded to github due to size reason, please contact Jiahua by u6162679@anu.edu.au for more information.

**Evaluation Function** 

Evaluation function can be found in fasttext_evaluate.ipynb created by Yilin. The functions are also integrated into v3 and v4.


