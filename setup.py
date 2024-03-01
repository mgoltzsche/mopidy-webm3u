import re
from setuptools import setup, find_packages


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-WebM3U',
    version=get_version('mopidy_webm3u/__init__.py'),
    url='https://github.com/mgoltzsche/mopidy-webm3u',
    license='Apache License, Version 2.0',
    author='Max Goltzsche',
    author_email='max.goltzsche@gmail.com',
    description='Mopidy plugin to play M3U playlists that are hosted on a web server',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 3.4.2',
        'Pykka >= 4.0.2',
    ],
    entry_points={
        'mopidy.ext': [
            'webm3u = mopidy_webm3u:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
