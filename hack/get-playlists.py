#!/usr/bin/env python3

import requests
import json

# Mopidy server URL
mopidy_url = 'http://localhost:6680/mopidy/rpc'

# JSON-RPC method to get playlists
method = 'core.playlists.get_playlists'

# JSON-RPC params
params = {'uri_scheme': 'm3u'}

# JSON-RPC request
payload = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': method,
    'params': params,
}

# Send the request to Mopidy
response = requests.post(mopidy_url, json=payload)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    result = response.json()

    # Extract playlists from the result
    print(result)
    playlists = result.get('result', [])

    # Print information about each playlist
    for playlist in playlists:
        print(f"Playlist Name: {playlist['name']}")
        print("Tracks:")
        for track in playlist['tracks']:
            print(f"  - {track['uri']}")
        print("\n")
else:
    print(f"Error: {response.status_code}, {response.text}")
