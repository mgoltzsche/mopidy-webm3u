import pykka
import hashlib
import logging
import typing
from pathlib import Path
from urllib.parse import urlparse
from mopidy import backend, models
from .m3u import parse_playlist
from .types import WebM3UConfig
from typing import cast, ClassVar

logger = logging.getLogger('mopidy_webm3u')

class WebM3UBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super().__init__()
        ext_config = cast(WebM3UConfig, config['webm3u'])
        uri_scheme = ext_config['uri_scheme']
        self.uri_schemes = [uri_scheme]
        self.playlists = WebM3UPlaylistsProvider(self, ext_config['seed_m3u'], uri_scheme)

class WebM3UPlaylistsProvider(backend.PlaylistsProvider):
    def __init__(self, backend, seed_m3u_url, uri_scheme):
        super().__init__(backend)
        self._seed_m3u_url = seed_m3u_url
        self._uri_scheme = uri_scheme
        self._playlist_refs = {}
        self.refresh()

    def as_list(self):
        logger.debug('Listing playlists')
        l = [p.ref for p in self._playlist_refs.values()]
        l.sort(key=lambda p: (p.name, p.uri))
        return l

    def get_items(self, uri):
        logger.debug('Getting playlist ltems')
        url = self._uri2url(uri)
        return [_item2ref(item) for item in parse_playlist(url)]

    def lookup(self, uri):
        logger.debug(f"Looking up playlist {uri}")
        pl = self._uri2playlistref(uri).ref
        url = self._uri2url(uri)
        tracks = [_item2track(item) for item in parse_playlist(url)]
        return models.Playlist(uri=uri, name=pl.name, tracks=tracks)

    def _uri2playlistref(self, uri):
        p = self._playlist_refs.get(uri)
        if not p:
            raise Exception(f"playlist {uri} not found")
        return p

    def refresh(self):
        logger.info(f"Loading M3U playlists from {self._seed_m3u_url}...")
        playlists = [self._playlistref(pl) for pl in parse_playlist(self._seed_m3u_url)]
        logger.info(f"Loaded {len(playlists)} M3U playlists from server")
        self._playlist_refs = {p.uri: p for p in playlists}

    def create(self, name):
        logger.warning('Playlist creation is not supported by this provider')

    def delete(self, uri):
        logger.warning('Playlist deletion is not supported by this provider')
        return False

    def save(self, uri):
        logger.warning('Playlist manipulation is not supported by this provider')

    def _uri2url(self, uri):
        assert uri.startswith(f"{self._uri_scheme}:playlist:"), 'unsupported URI format provided'
        return self._uri2playlistref(uri).url

    def _playlistref(self, item):
        filename = Path(urlparse(item.uri).path).stem
        urlhash = hashlib.sha256(item.uri.encode('utf-8')).hexdigest()[:7]
        id = f"{filename}-{urlhash}".strip('-.')
        uri = f"{self._uri_scheme}:playlist:{id}"
        return PlaylistRef(uri, item.uri, item.title)

def _item2track(item):
    return models.Track(
        uri=item.uri,
        name=item.title,
        genre=item.attrs.get('genre'),
        length=item.duration*1000,
    )

class PlaylistRef:
    def __init__(self, uri, url, name):
        self.uri = uri
        self.url = url
        self.ref = models.Ref(uri=uri, name=name, type=models.Ref.PLAYLIST)
