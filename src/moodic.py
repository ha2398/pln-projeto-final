#!/usr/bin/env python3

'''
Moodic
@author: Hugo Sousa
'''

import argparse
import mylast as ml
import lyricwikia as lw
import pylast
import sys

API_KEY = 'c9a7f0509e1be9ea5e8b1fce88bd1486'
API_SECRET = '93de978ac877b9c01079ce0cd32ae4ec'

###############################################################################


def add_args():	
	# Adds optional command line arguments to the program.
	parser = argparse.ArgumentParser()
	
	parser.add_argument('USERNAME', metavar='username', type=str,
		help='Name of the user to analyze')

	parser.add_argument('-n', dest='NSONGS', default=20, type=int,
		help='Number of last played songs to collect')

	return parser.parse_args()


def main():
	args = add_args()
	tracks = ml.get_recent_tracks(args.USERNAME, args.NSONGS)

	artist, song = str(tracks[0].track).split(' - ')
	print(artist, song)

	lyrics = lw.get_lyrics(artist, song)
	print(lyrics)

	return

main()
