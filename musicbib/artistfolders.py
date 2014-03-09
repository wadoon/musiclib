# -*- encoding: utf-8 -*- 
import os
import sys
import time
from urllib import FancyURLopener
import urllib2
import simplejson
from path import path
import requests
from PIL import Image
from gi.repository import Gio
from urllib import urlretrieve

accKey="l34lBJ1iR7RXmz19ZhazNyC7l/4EECHO8KFboNSAf7Q"

def set_folder_icon(folder, icon = "folder.jpg"):
    folder = Gio.File.new_for_path(folder)
    #icon_file = Gio.File.new_for_path(icon)

    info = folder.query_info('metadata::custom-icon', 0, None)

    info.set_attribute_string('metadata::custom-icon', icon)
    #else:
    #    info.set_attribute('metadata:.custom-icon', Gio.FileAttributeType.INVALID,'')
    folder.set_attributes_from_info(info, 0, None)



def prepareImage(url, folder):
    size = (256,256)
    tmp = "/tmp/folder.jpg"
    saved = folder + "/folder.jpg"

    #print "set %s for %s" % (url, folder)

    
    urlretrieve(url, saved)
    set_folder_icon(folder)
        #im =  Image.open(tmp)
        #im.thumbnail(size)
        #im.save(saved)        
    

    
def search_image(folder):
    
    searchTerm = folder.basename().replace(' ', '%20')
    url =r'https://api.datamarket.azure.com/Bing/Search/v1/Image?Query=%27the%20'+searchTerm+'%27&$format=json'
                
    
    resp = requests.get(url, auth = (accKey, accKey))
    print resp.content
    if resp.content and len(resp.content) > 0:
        tree = simplejson.loads(resp.content)                    
        url = tree['d']['results'][0]['MediaUrl']
        
        prepareImage(url, folder);
        print "FOUND" + str(folder)

    time.sleep(1);
    
        

folders = path(sys.argv[1]).dirs()
#from multiprocessing import Pool
#p = Pool(25)
map(search_image, folders)



