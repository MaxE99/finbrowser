class Article(object):

    def __init__(self, picture, title, link, pub_date):
        self.picture = picture
        self.title = title
        self.link = link
        self.pub_date = pub_date


def article_create(articles, favicon, title, link, pub_date):
    """Creates new article and appends it to list of articles."""
    new_article_instance = globals()['Article']
    instance = new_article_instance(favicon, title, link, pub_date)
    articles.append(instance)