from mako.template import Template
import traceback
import json
from flask import Flask,request
from controller import reddit_fetcher
import threading


app = Flask(__name__)

@app.route('/')
def get_images() :
    try :
        image_url_list = reddit_fetcher.get_list_of_images()
    except : 
        if reddit_fetcher.debug == True : 
            traceback.print_exc()
        return 'error'
    template = Template(filename='./view/template.txt')
    return template.render(url_list = image_url_list)


if __name__ == '__main__' :
    reddit_fetcher.refresh_image_list()
    app.run(debug=reddit_fetcher.debug)
