import requests as req
import sys
from io import StringIO
from bs4 import BeautifulSoup
import re
import threading


regex = re.compile('(.)*\.(gif|png|jpg)')
subreddit_root = 'http://reddit.com/r/'
subreddit_category = 'hot' 
response_format = 'json' 
im = []
inter = 0

#Generate a url for a subreddit given the name and the globals
def gen_url_for_subreddit(subreddit_name) :
    url = subreddit_root + subreddit_name + '/' + subreddit_category + '.' +   response_format
    return url

#Fetch json of reddit posts given the url 
def fetch_reddit_posts(reddit_url) :
    response = get_content_from_url(reddit_url)
    response.raise_for_status() 
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
    content  = req.get(url)
    #print('blah blah ' + content.status_code)
    return content 

#Returns a list of the image urls given the imgur url
def get_image_urls_from_imgur(imgurUrl) : 
    image_url_list = []
    for url in imgurUrl :
        content = get_content_from_url(url).text
        soup = get_dom(content)
        image_url_list = image_url_list + [img_div.select('img')[0]['src'] for img_div in soup.select('.post-image')]
    return image_url_list 

#Returns the list of image urls
def get_list_of_images() :
    global im
    return im

#Instantiate and return a BeautifulSoup object for the given html string
def get_dom(content) : 
    return BeautifulSoup(content,'html.parser') 

# Prepends a 'http' string to the url if one does not exist
def url_sanity_check(url) : 
    if url[0:4] != 'http' :
        url = 'http:' + url
    return url

def fetch_images_from_reddit(subreddit_name) :
    global im 
    reddit_url_list = fetch_reddit_posts(gen_url_for_subreddit(subreddit_name)) 
    imgur_site_urls = get_site_url_list(reddit_url_list)
    image_urls = get_img_url_list(reddit_url_list)
    image_urls = image_urls  + get_image_urls_from_imgur(imgur_site_urls)
    im = [url_sanity_check(url) for url in image_urls] 

def set_refresh_images_timer(interval) :
    inter = interval
    t = threading.Timer(interval,refresh_image_list)
    t.start()

def refresh_image_list() :
    fetch_images_from_reddit('aww')
    set_refresh_images_timer(inter) 
