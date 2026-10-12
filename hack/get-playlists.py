#!/usr/bin/env python3

import requests
import json

# Mopidy server URL
mopidy_url = 'http://localhost:6680/mopidy/rpc'

# First, get the list of playlists
method = 'core.playlists.as_list'
params = {}

# JSON-RPC request for playlist list
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
    print("Retrieved playlists:")
    playlists = result.get('result', [])
    
    if not playlists:
        print("No playlists found.")
    else:
        # For each playlist, get full details including tracks
        for i, playlist_ref in enumerate(playlists):
            print(f"\nPlaylist {i+1}:")
            print(f"Name: {playlist_ref.get('name', 'Unknown')}")
            print(f"URI: {playlist_ref.get('uri', 'Unknown')}")
            
            # Get full playlist details including tracks
            # We need to make another API call for this
            lookup_method = 'core.playlists.lookup'
            lookup_params = {'uri': playlist_ref.get('uri', '')}
            
            lookup_payload = {
                'jsonrpc': '2.0',
                'id': 2,
                'method': lookup_method,
                'params': lookup_params,
            }
            
            try:
                lookup_response = requests.post(mopidy_url, json=lookup_payload)
                if lookup_response.status_code == 200:
                    lookup_result = lookup_response.json()
                    full_playlist = lookup_result.get('result', {})
                    
                    if full_playlist:
                        print(f"Tracks: {len(full_playlist.get('tracks', []))}")
                        for j, track in enumerate(full_playlist.get('tracks', [])):
                            print(f"  Track {j+1}: {track.get('name', 'Unknown')} - {track.get('uri', 'Unknown')}")
                    else:
                        print("No track information available for this playlist")
                else:
                    print(f"Error retrieving playlist details: {lookup_response.status_code}")
            except Exception as e:
                print(f"Error making lookup call: {e}")
                
    print("\nDone.")
else:
    print(f"Error retrieving playlists: {response.status_code}, {response.text}")
