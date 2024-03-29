****************
Mopidy-WebM3U
****************

`Mopidy <https://mopidy.com/>`_ extension for reading M3U playlists from an HTTP server.

For example it allows you to browse and listen to the playlists within your `Beets <https://beets.io>`_ library that have been generated by Beets' `smartplaylist plugin <https://beets.readthedocs.io/en/stable/plugins/smartplaylist.html>`_ and served by the `beets-webm3u <https://github.com/mgoltzsche/beets-webm3u>`_ plugin (on another machine) within Mopidy.

This extension does not support manipulating playlists.


Installation
============

Install by running::

    sudo pip install Mopidy-WebM3U


Configuration
=============

Before starting Mopidy, you must configure it as follows, enabling the webm3u extension and specifying the URL to the M3U playlist of playlists::

    [m3u]
    enabled = false
    [webm3u]
    enabled = true
    seed_m3u = http://beets:8337/playlists/index.m3u
    uri_scheme = m3u


(Mopidy's built-in m3u extension must be disabled in order to be able to use the ``m3u`` URI scheme with the webm3u extension which is required to make playlists show up within the Iris web GUI, see `here <https://github.com/jaedb/Iris/blob/62c4e063f855896d2b4de8dcc024a43f967d5b67/src/js/util/helpers.js#L144>`_.)

The playlist of playlists URL specified by the ``seed_m3u`` option is expected to return an `EXTM3U-formatted <https://datatracker.ietf.org/doc/html/rfc8216#section-4.3.1.1>`_ list of `tagged <https://datatracker.ietf.org/doc/html/rfc8216#section-4.3.2.1>`_ `*.m3u` HTTP URLs, e.g.::

    #EXTM3U
    #EXTINF:0,Playlist 1
    http://localhost:8337/playlists/playlist1.m3u
    #EXTINF:0,Playlist 2
    http://localhost:8337/playlists/playlist2.m3u


Development
===========

First make sure an example M3U playlist of playlists is served at ``http://localhost:8337/m3u/playlists/index.m3u``, e.g. by running the `beets-webm3u development server <https://github.com/mgoltzsche/beets-container?tab=readme-ov-file#run-the-beets-web-server>`_.

Then you can run a mopidy container with the extension installed (including your local changes) as follows (requires `docker <https://docs.docker.com/engine/install/>`_)::

    make run


Once Mopidy started, you can browse the playlists within the Iris UI at `http://localhost:6680/iris/library/playlists <http://localhost:6680/iris/library/playlists>`_.

