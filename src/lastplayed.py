#!/usr/bin/env python
'''
Show 20 last played tracks, or all the last played tracks of an artist
(and optionally track)
'''
from __future__ import print_function
import argparse
import pylast
import sys
from mylast import (
    lastfm_network,
    lastfm_username,
    print_it,
    print_track,
    split_artist_track,
    TRACK_SEPARATOR,
    unicode_track_and_timestamp)


def get_recent_tracks(username, number):
    recent_tracks = lastfm_network.get_user(
        username).get_recent_tracks(limit=number)
    for i, track in enumerate(recent_tracks):
        printable = unicode_track_and_timestamp(track)
        print_it(str(i+1) + ' ' + printable)
    return recent_tracks


def get_artist_tracks(username, artist, title):
    if TRACK_SEPARATOR in artist:
        (artist, title) = split_artist_track(artist)

    print('Searching Last.fm library...\r',)
    try:
        tracks = lastfm_network.get_user(
            username).get_artist_tracks(artist=artist)
    except Exception as e:
        sys.exit('Exception: ' + str(e))

    total = 0

    print('\t\t\t\t\r'),  # clear line
    if title is None:  # print all
        for track in tracks:
            print_track(track)
        total = len(tracks)

    else:  # print matching titles
        find_track = pylast.Track(artist, title, lastfm_network)
        for track in tracks:
            if str(track.track).lower() == str(find_track).lower():
                print_track(track)
                total += 1

    print('Total:', total)
    return total