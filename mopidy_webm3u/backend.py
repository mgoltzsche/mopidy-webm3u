import pykka
import logging
import typing
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

# TODO: Protected URI against server-side request forgery - by enforcing hostname and path prefix for playlist URLs?!

class WebM3UPlaylistsProvider(backend.PlaylistsProvider):
    def __init__(self, backend, seed_m3u_url, uri_scheme):
        super().__init__(backend)
        self._seed_m3u_url = seed_m3u_url
        self._uri_scheme = uri_scheme
        self._playlist_refs = []
        self.refresh()

    def as_list(self):
        logger.debug('Listing playlists')
        return self._playlist_refs

    def get_items(self, uri):
        logger.debug('Getting playlist ltems')
        url = self._uri2url(uri)
        return [_item2ref(item) for item in parse_playlist(url)]

    def lookup(self, uri):
        logger.debug(f"Looking up playlist {uri}")
        pl = self._uri2playlistref(uri)
        url = self._uri2url(uri)
        tracks = [_item2track(item) for item in parse_playlist(url)]
        return models.Playlist(uri=uri, name=pl.name, tracks=tracks)

    def _uri2playlistref(self, uri):
        for pl in self._playlist_refs:
            if pl.uri == uri:
                return pl
        raise Exception(f"playlist {uri} not found")

    def refresh(self):
        logger.info(f"Loading M3U playlists from {self._seed_m3u_url}...")
        playlists = [self._playlistref(pl) for pl in parse_playlist(self._seed_m3u_url)]
        logger.info(f"Loaded {len(playlists)} M3U playlists from server")
        self._playlist_refs = playlists

    def create(self, name):
        logger.warning('Playlist creation is not supported by this provider')

    def delete(self, uri):
        logger.warning('Playlist deletion is not supported by this provider')
        return False

    def save(self, uri):
        logger.warning('Playlist manipulation is not supported by this provider')

    def _uri2url(self, uri):
        assert uri.startswith(f"{self._uri_scheme}:"), 'unsupported URI format provided'
        return uri[len(self._uri_scheme)+1:]

    def _playlistref(self, item):
        uri = f"{self._uri_scheme}:{item.uri}"
        return models.Ref(uri=uri, name=item.title, type=models.Ref.PLAYLIST)

def _item2track(item):
    return models.Track(
        uri=item.uri,
        name=item.title,
        genre=item.attrs.get('genre'),
        length=item.duration*1000,
    )
