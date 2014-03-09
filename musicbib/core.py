#!/usr/bin/python
#-*- encoding: utf-8 -*-

from __future__ import print_function

import shelve
import os.path, sys, os, random
import codecs
from progressbar import ProgressBar, AnimatedMarker, Percentage, FormatLabel, BouncingBar
from path import path

try:
    import ansi
    t = ansi.term()
    print = t.printr
except:
    pass


def create_progressbar(job_name, maxval):
    widgets = [job_name, " ",
               BouncingBar(),
               Percentage(),                        
               FormatLabel('Processed: %(value)d files (in: %(elapsed)s)')]
    return ProgressBar(widgets = widgets, maxval = maxval)

# try:
#     from colors import cprintln as cprint, register_tag
#     register_tag('debug',      fg="yellow")
#     register_tag('metaerror',  style="underline")
#
#     register_tag('title',  fg="blue")
#     register_tag('track',  fg="white")
#
#     register_tag('info', fg="blue", style="bold")
#     register_tag('error',fg="red", style="bold")
# except ImportError, e:
#     print(e)
#     cprint = print

from tag import *

class Indexer(object):
    def __init__(self, folder):
        self.db = shelve.open("mp3.db")
        self.folder = folder
        self.tags = None


    def readtags(self):
        self.tags = []
        files = gather_files(self.folder)
        pbar = create_progressbar("read tags", len(files))
        
        for fil in pbar(files):            
            t = extractTag(fil)            

            if t:
                self.tags.append(t)                    
            else:                
                print("{error  %s}" % fil)

        #self.db['songs'] = self.tags
        #print("{info read %d files}" % len(self.tags))
        return self.tags

    def fromDB(self):
        self.tags = self.db['songs']
        return self.tags

class LibraryCreator(object):
    def __init__(self, songs):
        self.albums = aggregate(songs)
        self.compilation_base = u"_Compilation"
        self.compilation_format = u"{base}/{year}-{album}/"
        self.album_format = u"{artist}/{year}-{album}/"
        self.album_processor = [self.forward_songs]
        self.finish_processors = []

    def format_song(self, s):
        if s.track:
            name = u"%02d. " % s.track
        else:
            name = u""

        try:
            title = s.title.replace("/", "_")
        except:
            title = u"not-set-%d" % (random.randint(1,100))
            print("{metaerror {title %s}}" % (s.path))

        a, suffix = os.path.splitext(s.path)
        return name + unicode(title) + suffix

    def forward_songs(self, album):
        mkdir(album.newplace)
        for s in album.songs:
            new  =   album.newplace / self.format_song(s)
            old  =   s.path
            s.newpath = new
            forward_file(old, new)
        #oldAlbumPath = os.path.dirname(songs[0].path)
        #forward_files( path(oldAlbumPath) , path(albumRoot))

    def format_compilation(self, track):
        d = track.as_dict()
        d["base"] = self.compilation_base
        return (self.compilation_format.format(**d))

    def format_album(self, track):
        d = track.as_dict()
        d["base"] = self.compilation_base
        return (self.album_format.format(**d))

    def built_into(self, folder):
        folder = path(folder)
        pbar = create_progressbar("buit new music folder", 0);

        for album in pbar(self.albums.values()):
            if album.is_collection:
                name = self.format_compilation(album.songs[0])
            else:
                name = self.format_album(album.songs[0])
            album.newplace = folder / name

            self.process_album(album)
        self.process_finish()

    def process_finish(self):
        for processor in self.finish_processors:
            processor()

    def process_album(self, album):
        for processor in self.album_processor:
            processor(album)

class PlaylistCreator(object):
    def __init__(self, f):
        self.artist = {}
        self.album = []
        self.target_folder = path(f)

    def __call__(self, album):
        artist=album.songs[0].artist
        try:
            self.artist[artist] += album.songs
        except KeyError:
            self.artist[artist] = list(album.songs)
        self.album.append(album)

    def finish(self):
        pbar = create_progressbar("create artist playlists", len(self.artist))
        for artist, songs in pbar(self.artist.items()):
            artist_playlist = self.target_folder / ("%s-all.m3u" % artist)
            with codecs.open(artist_playlist, 'w', encoding="utf-8") as m3u:
                names = map(lambda x: x.newpath, songs)
                names.sort()
                m3u.write("\n".join(names))

        pbar = create_progressbar("create album playlists", len(self.album))
        for album in self.album:
            album_playlist = album.newplace / "00-playlist.m3u"
            with codecs.open(album_playlist, 'w', encoding="utf-8") as m3u:
                names = map(lambda x: x.newpath, album)
                names.sort()
                m3u.write("\n".join(names))
                m3u.close()

def aggregate(songs):
    pbar = ProgressBar()
    albums = {}

    for tag in pbar(songs):
        try:
            a = tag.album.strip().lower()
        except:
            a = "empty-album"

        try:
            albums[a].add(tag)
        except KeyError as e:

            album = Album(name = tag.album, songs = [tag])
            albums[a] = album

    #print("Found: %d albums" % len(albums))
    return albums


def mkdir(p):
    """
    save wrapper for os.mkdir
    """

    try: 
        os.makedirs(p)
    except OSError as e:
        pass
    return

def forward_file(src,dest):    
    try:
        os.link(os.path.abspath(src),os.path.abspath(dest))
    except OSError as e:
        pass #cprint("{error could not link %s to %s (%s)" %(musicbib,dest, e))

def forward_files(old, new):
    for fil in old.files("*.jpg"):
        a = os.path.join(new, fil.basename())
        forward_file(fil,a)    


class AlbumFolder(object):
    def __init__(self):
        self.search_names = ["album.jpg", "folder.jpg", "*.png", "*.jpg"]

    def find_icon(self, album):
        for s in album.songs:
            folder = s.path.dirname()
            if isinstance(folder, (unicode, str)):
                folder = path(folder);
            for name in self.search_names:
                files = folder.files(pattern = name)
                if files:
                    return files[0]
        return None

    def __call__(self, album):
        icon = self.find_icon(album)
        if icon:
            icon = os.path.abspath(icon)
            forward_file(icon, album.newplace)
            icon = os.path.basename(icon)
            set_folder_icon(album.newplace, icon)
            print("{info set_folder_icon %s for %s}" % (icon, album.newplace))


import urllib2, urllib
def download_image_to_filename(artist, album, dest_filename):
    # Returns False if no images found
    imgfound = False
    img_url = ""
    # Amazon currently doesn't support utf8 and suggests latin1 encoding instead:
    try:
        artist = urllib.quote(artist.encode('latin1'))
        album = urllib.quote(album.encode('latin1'))
    except:
        artist = urllib.quote(artist)
        album = urllib.quote(album)
    amazon_key = "12DR2PGAQT303YTEWP02"
    search_url = "http://webservices.amazon.com/onca/xml?" \
                 + "Service=AWSECommerceService&AWSAccessKeyId=" \
                 + amazon_key \
                 + "&Operation=ItemSearch&SearchIndex=Music&Artist="\
                 + artist \
                 + "&ResponseGroup=Images&Keywords=" \
                 + album
    request = urllib2.Request(search_url)
    opener = urllib2.build_opener()
    f = opener.open(request).read()
    curr_pos = 300    # Skip header..
    curr_pos = f.find("<LargeImage>", curr_pos+10)
    url_start = f.find("<URL>http://", curr_pos)+len("<URL>")
    url_end = f.find("</URL>", curr_pos)
    img_url = f[url_start:url_end]
    urllib.urlretrieve(img_url, dest_filename)
    imgfound = True
    return imgfound



def set_folder_icon(folder, icon = "folder.jpg"):
    from gi.repository import Gio
    folder = Gio.File.new_for_path(folder)
    #icon_file = Gio.File.new_for_path(icon)

    info = folder.query_info('metadata::custom-icon', 0, None)
    info.set_attribute_string('metadata::custom-icon', icon)
    #else:
    #    info.set_attribute('metadata:.custom-icon', Gio.FileAttributeType.INVALID,'')
    folder.set_attributes_from_info(info, 0, None)


