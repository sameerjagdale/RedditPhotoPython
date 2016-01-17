from mako.template import Template
from flask import Flask
from controller import reddit_fetcher
import threading


app = Flask(__name__)

@app.route('/')
def get_images() :
    try :
        image_url_list = reddit_fetcher.get_list_of_images()
    except : 
        return 'error', status.HTTP_404_NOT_FOUND
    template = Template(filename='./view/template.txt')
    return template.render(url_list = image_url_list)

if __name__ == '__main__' :
    reddit_fetcher.fetch_images_from_reddit('aww')
    reddit_fetcher.set_refresh_images_timer(24 * 3600)
    app.run()
