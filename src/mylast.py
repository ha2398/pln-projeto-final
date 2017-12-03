#!/usr/bin/env python
# coding: utf-8

import os
import pylast
import sys

try:
    API_KEY = os.environ['LASTFM_API_KEY']
    API_SECRET = os.environ['LASTFM_API_SECRET']
except KeyError:
    API_KEY = 'c9a7f0509e1be9ea5e8b1fce88bd1486'
    API_SECRET = '93de978ac877b9c01079ce0cd32ae4ec'

try:
    lastfm_username = os.environ['LASTFM_USERNAME']
    lastfm_password_hash = os.environ['LASTFM_PASSWORD_HASH']
except KeyError:
    # In order to perform a write operation you need to authenticate yourself
    lastfm_username = 'sousah'
    lastfm_password_hash = 'e696ac4131308968602a83ce41b2a027'


lastfm_network = pylast.LastFMNetwork(
    api_key=API_KEY, api_secret=API_SECRET,
    username=lastfm_username, password_hash=lastfm_password_hash)


# Windows cmd.exe cannot do Unicode so encode first
def print_it(text):
    print(text.encode('utf-8'))


def unicode_track_and_timestamp(track):
    unicode_track = unicode(str(track.track), 'utf8')
    return track.playback_date + '\t' + unicode_track


def print_track(track):
    print_it(unicode_track_and_timestamp(track))


TRACK_SEPARATOR = u' - '


def split_artist_track(artist_track):
    artist_track = artist_track.replace(u' – ', ' - ')
    artist_track = artist_track.replace(u'“', '\'')
    artist_track = artist_track.replace(u'”', '\'')

    (artist, track) = artist_track.split(TRACK_SEPARATOR)
    artist = artist.strip()
    track = track.strip()
    print_it('Artist:\t\t'' + artist + ''')
    print_it('Track:\t\t'' + track + ''')

    # Validate
    if len(artist) is 0 and len(track) is 0:
        sys.exit('Error: Artist and track are blank')
    if len(artist) is 0:
        sys.exit('Error: Artist is blank')
    if len(track) is 0:
        sys.exit('Error: Track is blank')

    return (artist, track)