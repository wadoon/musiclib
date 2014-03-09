__author__ = 'weigl'


class Song(object):
    def __init__(self, title=None, artist=None, tracknumber=None, year=None, path=None, album=None, date=None):
        self.title = title
        self.artist = artist
        self.track = tracknumber
        self.year = year or date
        self.path = path
        self.album = album

    def as_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "track": self.track,
            "year": self.year,
            "path": self.path,
            "album": self.album
        }

    @property
    def title(self):
        return self._title

    @property
    def artist(self):
        return self._artist

    @property
    def track(self):
        return self._track

    @property
    def year(self):
        return self._year

    @property
    def path(self):
        return self._path

    @property
    def album(self):
        return self._album

    @title.setter
    def title(self, title):
        self._title = title

    @artist.setter
    def artist(self, a):
        self._artist = a

    @track.setter
    def track(self, t):
        self._track = t

    @year.setter
    def year(self, y):
        self._year = y

    @path.setter
    def path(self, p):
        self._path = p

    @album.setter
    def album(self, a):
        self._album = a


class Album(object):
    def __init__(self, name=None, songs=None):
        if songs:
            self._songs = list(songs)
        else:
            self._songs = []

        self._name = name

    def __iter__(self):
        return iter(self._songs)

    def add(self, song):
        self._songs.append(song)

    @property
    def songs(self):
        return self._songs

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def is_collection(self):
        "True iff. the songs belong to a collection iff. the artists are different"
        artists = [s.artist for s in self.songs]
        for i in range(len(artists) - 1):
            if artists[i] != artists[i + 1]:
                return True
        return False