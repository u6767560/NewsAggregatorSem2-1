class FastTextRankEntity:
    def __init__(self, news_id, cleaned_text, rank=0):
        self.news_id = news_id
        self.cleaned_text = cleaned_text
        self.rank = rank

