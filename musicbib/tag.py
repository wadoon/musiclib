__author__ = 'weigl'

from mutagen import mp3, flac
import mutagen

from .model import *

SFX = {"mp3": mp3, "flac": flac, }
MUSIC_FILE_PATTERNS = ('*.mp3', '*.ogg', '*.flac')

def is_music_file(fil):
    return any((fil.fnmatch(pattern) for pattern in MUSIC_FILE_PATTERNS))


def gather_files(folder):
    if isinstance(folder, str):
        folder = path(folder)

    files = folder.walkfiles(errors = "warn")
    return [f for f in files if is_music_file(f)]


def extractTag(fname):
    keys = ["album", "artist", "title", "tracknumber", "date"]

    try:
        tag = mutagen.File(fname, easy=True)

        def get(k):
            try:
                return tag[k][0]
            except KeyError:
                return None

        d = {k: get(k) for k in keys}
        d["path"] = fname

        return Song(**d)
    except Exception, e:
        print "Could not read tag from file %s" % fname, e
        return None

    # #print("\r SCAN: %s" % fname)
    # try:
    #     if fname.endswith("mp3"):
    #         audiofile = eyed3.load(fname)
    #
    #         try:
    #             year = audiofile.tag.release_date.year
    #         except:
    #             try:
    #                 year = audiofile.tag.recording_date.year
    #             except:
    #                 year = 0
    #
    #         return Song(
    #             path = fname,
    #             album = audiofile.tag.album,
    #             artist = audiofile.tag.artist,
    #             title =  audiofile.tag.title,
    #             track =  audiofile.tag.track_num[0],
    #             year = year )
    #     elif fname.endswith('flac'):
    #         audiofile = flac.Open(fname)
    #         return Song(
    #             path = fname,
    #             album = audiofile["album"][0],
    #             artist = audiofile['artist'][0],
    #             title =  audiofile['title'][0],
    #             track =  int(audiofile['tracknumber'][0]),
    #             year = audiofile['date'][0])
    #     else:
    #         audiofile = audio.File(fname)
    #         return Song(
    #             path = fname,
    #             album = audiofile.album,
    #             artist = audiofile.artist,
    #             title =  audiofile.title,
    #             track =  audiofile.track,
    #             year = audiofile.year)
    # except Exception as e:
    #     print("EXCEPTION", e)
    #     return None

