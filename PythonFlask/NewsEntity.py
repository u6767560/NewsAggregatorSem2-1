class NewsEntity:
    def __init__(self, title, authors, publish_date, meta_description,meta_keywords, cleaned_text, url,
                 category="Global"):
        self.title = title
        self.authors = authors
        self.publish_date = publish_date
        self.meta_description = meta_description
        self.cleaned_text = cleaned_text
        self.meta_keywords = meta_keywords
        self.url = url
        self.category = category
