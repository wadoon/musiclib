__author__ = 'weigl'

import docopt

_documentation = """
Music Bib Manager -- Alexander Weigl 2014

Usage:
  mscbb create [-e <error>] <src> <dest>

Options:

"""

from .core import *

def main():
    #keys = docopt.docopt(_documentation, "mscbb create -e x.log src dest".split(" "))
    #print keys

    src = path("/home/weigla/Documents/music/Toten Hosen/")
    dest = path("/home/weigla/tmp/musc")

    idx = Indexer(src)
    idx.readtags()

    builder = LibraryCreator(idx.tags)
    plc = PlaylistCreator(dest)
    afdr = AlbumFolder()

    builder.album_processor.append(plc)
    builder.album_processor.append(afdr)
    builder.finish_processors.append(plc.finish)
    builder.built_into(dest)

