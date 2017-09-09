#!/usr/bin/env python

'''
Moodic
@author: Hugo Sousa
'''

import lastplayed as lp
import pylast
import sys

API_KEY = 'c9a7f0509e1be9ea5e8b1fce88bd1486'
API_SECRET = '93de978ac877b9c01079ce0cd32ae4ec'

###############################################################################

def main():
    if len(sys.argv) != 3:
        return

    username = sys.argv[1]
    n_songs = int(sys.argv[2])
    lp.get_recent_tracks(username, n_songs)

main()