# -*- coding: utf-8 -*-
import urllib2
import urllib
import json

API_KEY = '6a07c6bba0c168728370ac95edb65219'
API_ENDPOINT = 'http://ws.audioscrobbler.com/2.0/'


def parse_filename(filename):
    artist_track = filename[:filename.find(".")].split("-")
    if len(artist_track) != 2:
        return False

    return artist_track[0].strip(), artist_track[1].strip()


def get_top_tag(filename):
    res = parse_filename(filename)
    if not res:
        return False

    artist, track = res

    req_query = {
        'method': "track.getInfo",
        'api_key': API_KEY,
        'artist': artist,
        'track': track,
        'format': "json"
    }
    url_values = urllib.urlencode(req_query)
    full_url = API_ENDPOINT + '?' + url_values
    response = urllib2.urlopen(full_url)
    data = json.load(response)
    try:
        top_tag = data["track"]["toptags"]["tag"][0]["name"]
        return top_tag
    except:
        return "unknown"

if __name__ == '__main__':
    print get_top_tag("The Beatles - Yellow Submarine.mp3") == 'classic rock'
    print get_top_tag("Metallica - Whiskey in the Jar.mp3") == 'metal'
    print get_top_tag("No Te Va Gustar - Chau.mp3") == 'rock'
    print get_top_tag("Daft Punk - Doin' It Right.mp3")
    print get_top_tag("Daft Punk - Get Lucky.mp3")
