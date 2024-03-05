import logging
import os

from mopidy import config, ext


__version__ = '0.1.0'

# If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-WebM3U'
    ext_name = 'webm3u'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['seed_m3u'] = config.String()
        schema['uri_scheme'] = config.String()
        return schema

    def setup(self, registry):
        # Register the backend
        from .backend import WebM3UBackend
        registry.add('backend', WebM3UBackend)

        # Register a frontend
        #from .frontend import SoundspotFrontend
        #registry.add('frontend', SoundspotFrontend)
