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

TRACK_SEPARATOR = ' - '

def get_recent_tracks(username, number):
    recent_tracks = lastfm_network.get_user(
        username).get_recent_tracks(limit=number+1)
    for i, track in enumerate(recent_tracks):
        printable = track.playback_date + ' - ' + str(track.track)
        print(str(i+1) + ' ' + printable)
    return recent_tracks