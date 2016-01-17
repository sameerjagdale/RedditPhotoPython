import requests as req
import sys
from io import StringIO
from bs4 import BeautifulSoup
import re
from mako.template import Template
from flask import Flask

regex = re.compile('(.)*\.(gif|png|jpg)')
subreddit_root = 'http://reddit.com/r/'
subreddit_category = 'hot' 
response_format = 'json' 

#Generate a url for a subreddit given the name and the globals
def gen_url_for_subreddit(subreddit_name) :
    url = subreddit_root + subreddit_name + '/' + subreddit_category + '.' +   response_format
    return url

#Fetch json of reddit posts given the url 
def fetch_reddit_posts(reddit_url) :
    response = get_content_from_url(reddit_url)
    #del(response.json()['data']['children'][0])
    #response.json()['data']['children'].pop()
    urlList = [x['data']['url'] for x in response.json()['data']['children'][1:]] 
    return urlList

#Filters out the list of urls which are link to a imgur page
def get_site_url_list(urlList) :
    return [url for url in urlList if regex.match(url) == None]

#Filters out the list of urls which are link to the images
def get_img_url_list(urlList) :
    return [url for url in urlList if regex.match(url) != None]

#Returns the content of a webpage given its url
def get_content_from_url(url) :
    return req.get(url)

#Returns a list of the image urls given the imgur url
def get_image_urls_from_imgur(imgurUrl) : 
    image_url_list = []
    for url in imgurUrl :
        content = get_content_from_url(url).text
        soup = get_dom(content)
        image_url_list = image_url_list + [img_div.select('img')[0]['src'] for img_div in soup.select('.post-image')]
    return image_url_list 

def get_list_of_img_urls(subreddit_name) :
    reddit_url_list = fetch_reddit_posts(gen_url_for_subreddit(subreddit_name)) 
    imgur_site_urls = get_site_url_list(reddit_url_list)
    image_urls = get_img_url_list(reddit_url_list)
    image_urls = image_urls  + get_image_urls_from_imgur(imgur_site_urls)
    return image_urls 

#Instantiate and return a BeautifulSoup object for the given html string
def get_dom(content) : 
    return BeautifulSoup(content,'html.parser') 

def url_sanity_check(url) : 
    if url[0:4] != 'http' :
        url = 'http:' + url
    return url

app = Flask(__name__)

@app.route('/')
def get_images() :
    image_url_list = [url_sanity_check(url) for url in get_list_of_img_urls('aww')]
    template = Template(filename='template.txt')
    return template.render(url_list = image_url_list)

if __name__ == '__main__' :
    app.run()
