import scrapy
import requests
import string
import csv
from bs4 import BeautifulSoup

class dataPoint:
    def __init__(self, slyFactor, date):
        self.slyFactor = slyFactor
        self.date = date
    def showData(self):
        print(self.date + ', ' + str(self.slyFactor))
        
#function to parse a bbc news blog link (takes hlink string and querylist string array as arguments, returns dataPoint)
def blog_parser(hlink, querylist):
    subURL = requests.get('https://www.bbc.com' + str(hlink))
    subSoup = BeautifulSoup(subURL.content, 'html.parser')
    dateT = (subSoup.find('div', class_='date date--v2')).get_text()
    content = subSoup.find_all('p')
    counter = 0
        
    for p in content:
        text = p.get_text()
        replace_punctuation = str.maketrans(string.punctuation, ' '*len(string.punctuation))
        text = text.translate(replace_punctuation)
        wordlist = text.split()
        for query in querylist:
            counter = counter + wordlist.count(query)
        
    data_p = dataPoint(counter, dateT)
    return data_p

#list of words to determine immigration saliency:
query_list = ['immigration', 'immigrant', 'immigrants', 'migration', 'migrant', 'migrants', 'refugee', 'refugees']

class NewsSpider(scrapy.Spider):
    name = 'news_spider'
    start_urls = ['https://www.bbc.com/news/blogs/the_papers']
    
    def __init__(self):
        self.outfile = open("dataset.csv", "w", newline="")
        self.writer = csv.writer(self.outfile)
        self.writer.writerow(['Date', 'Saliency Count'])
        print("***"*20,"opened")
        
    def closed(self,reason):
        self.outfile.close()
        print("***"*20,"closed")
    
    def parse(self, response):
        
        news_blogs = response.css('div.blog__story.story-inner')
        
        for blog in news_blogs:
            link = blog.css('a::attr(href)').get()
            data_point = blog_parser(link, query_list)
            self.logger.info(data_point.showData())
            self.writer.writerow([data_point.date, str(data_point.slyFactor)])
            
        next_page = response.css('div.blog__stories.story-body::attr(data-next)').get()
        if next_page is not None:
            yield scrapy.Request('https://www.bbc.com' + str(next_page), callback = self.parse)
    