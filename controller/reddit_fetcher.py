import requests as req
import time
import sys
from io import StringIO
from bs4 import BeautifulSoup
import re
import threading
import json


regex = re.compile('(.)*\.(gif|png|jpg)')
subreddit_root = 'http://reddit.com/r/'
subreddit_category = 'hot' 
response_format = 'json' 
im = {}
inter = 0
debug = True
headers = {'user-agent': 'reddit-slideshow-0.0.1'}
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
    content  = req.get(url, headers = headers)
    return content 

#Returns a list of the image urls given the imgur url
def get_image_urls_from_imgur(imgurUrl) : 
    image_url_list = []
    for url in imgurUrl :
        content = get_content_from_url(url).text
        soup = get_dom(content)
        for img_div_list in soup.select('.post-image') :
            if len(img_div_list) == 0 : 
                continue
            img_div = img_div_list.select('img')
            if  len(img_div) == 0:
                continue
            image_url_list.append(img_div[0]['src'])
    return image_url_list 

#Returns the list of image urls
def get_list_of_images(subreddit_name = 'aww') :
    global im
    if debug == True : 
        print('Returning images fetched at {:f}'.format(im['timestamp']))
    return im[subreddit_name]

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
    im[subreddit_name] = [url_sanity_check(url) for url in image_urls]
    im['timestamp'] = time.time() 

def set_refresh_images_timer(interval) :
    global inter
    inter = interval
    t = threading.Timer(interval,refresh_image_list)
    t.start()

def refresh_image_list() :
    wait_time = 60
    with open('subreddit_list.json','r') as sbl : 
        x = json.load(sbl) 
        subreddit_name_list  = x['subreddit_names']
        print(len(subreddit_name_list))
        for subreddit in subreddit_name_list :
            while(True) :
                try :
                    if debug == True : 
                        print('Fetching images for ' + subreddit)
                    fetch_images_from_reddit(subreddit)
                    break
                except : 
                    if debug == True : 
                        print('Error 429')
                    time.sleep(wait_time)
                    wait_time = wait_time * 2
                    continue
            wait_time = 60
            time.sleep(60)
    set_refresh_images_timer(24 * 3600) 
