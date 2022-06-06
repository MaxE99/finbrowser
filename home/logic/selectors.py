# Python imports
import html
from datetime import datetime

def article_components_get(item):
    """Goes through xml item and returns title, link and publishing date of article."""

    # some titles in the xml files have been escaped twice which makes it necesseary to ecape the titles more than once
    def double_escaped_string_unescape(title):
        unescaped = ""
        while unescaped != title:
            title = html.unescape(title)
            unescaped = html.unescape(title)
        return title

    title = double_escaped_string_unescape(item.find('.//title').text)
    link = item.find('.//link').text
    pub_date = item.find('.//pubDate').text[:-4]
    pub_date = datetime.strptime(pub_date.replace(" -", ""), '%a, %d %b %Y %X')
    return title, link, pub_date