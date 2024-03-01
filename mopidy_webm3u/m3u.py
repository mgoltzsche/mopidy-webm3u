import re
import requests

_extinf_regex = re.compile(r'^#EXTINF:([0-9]+)( [^,]+)?,[\s]*(.*)')

def parse_playlist(url):
    # CAUTION: attribute values that contain ',' or ' ' are not supported
    # TODO: use mopidy http client/proxy config, see https://docs.mopidy.com/en/latest/extensiondev/#making-http-requests-from-extensions
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        linenum = 0
        item = PlaylistItem()
        for lineb in resp.iter_lines():
            line = lineb.decode('utf-8')
            line = line.rstrip()
            linenum += 1
            if linenum == 1:
                assert line == '#EXTM3U', 'File is not an EXTM3U playlist!'
                continue
            if len(line.strip()) == 0:
                continue
            m = _extinf_regex.match(line)
            if m:
                item = PlaylistItem()
                duration = m.group(1)
                item.duration = int(duration)
                attrs = m.group(2)
                if attrs:
                    item.attrs = {k: v.strip('"') for k,v in [kv.split('=') for kv in attrs.strip().split(' ')]}
                else:
                    item.attrs = {}
                item.title = m.group(3)
                continue
            if line.startswith('#'):
                continue
            item.uri = line
            yield item
            item = PlaylistItem()

class PlaylistItem():
    def __init__(self):
        self.title = None
        self.duration = None
        self.uri = None
        self.attrs = None
