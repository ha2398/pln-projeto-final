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

from langdetect import detect
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tqdm import tqdm

API_KEY = 'c9a7f0509e1be9ea5e8b1fce88bd1486'
API_SECRET = '93de978ac877b9c01079ce0cd32ae4ec'


negative_emotions = ['anger', 'disgust', 'fear', 'negative', 'sadness']


###############################################################################


def add_args():	
	# Adds optional command line arguments to the program.
	parser = argparse.ArgumentParser()
	
	parser.add_argument('USERNAME', metavar='username', type=str,
		help='Name of the user to analyze')

	parser.add_argument('LEXICON', metavar='lexicon', type=str,
		help='Name of the emotion lexicon file')

	parser.add_argument('-n', dest='NSONGS', default=20, type=int,
		help='Number of last played songs to collect')

	return parser.parse_args()


def load_emolex(emolex_filename):

	emolex_file = open(emolex_filename, 'r')

	emolex = {}
	print('[+] Loading emotion lexicon')
	for line in emolex_file:
		word, emotion, activation = line.split()

		if activation == '0':
			continue
		elif emotion in emolex:
			emolex[emotion].append(word)
		else:
			emolex[emotion] = [word]

	for emotion in emolex:
		emolex[emotion] = set(emolex[emotion])

	emolex_file.close()
	return emolex


def filter_english(song_lyrics):
	print('[-] Removing non-english lyrics')
	for song in tqdm(song_lyrics):
		if detect(song_lyrics[song]) != 'en':
			del song_lyrics[song]


def download_lyrics(tracks):
	song_lyrics = {}
	print('[+] Downloading lyrics')
	for i in tqdm(range(len(tracks))):
		temp = str(tracks[i].track).split(' - ')
		artist, song = temp[0], temp[1]

		try:
			lyrics = lw.get_lyrics(artist, song)

			if len(lyrics.split()) != 1: # Non-instrumental
				song_lyrics[' - '.join([artist, song])] = lyrics
		except:
			pass

	return song_lyrics


def quantify_negativeness(lyrics, emolex):
	wnl = WordNetLemmatizer()

	negative_pct = {}
	stop_words = set(stopwords.words('english'))

	for song in lyrics:
		tokens = [t for t in word_tokenize(lyrics[song]) if t not in stop_words]
		tokens = set([wnl.lemmatize(t) for t in tokens])
		print(song, tokens)
		total_tokens = len(tokens)
		negative_tokens = 0

		for token in tokens:
			for emotion in negative_emotions:
				if token in emolex[emotion]:
					negative_tokens += 1
					break

		negative_pct[song] = negative_tokens/total_tokens

	return negative_pct


def main():
	args = add_args()

	print('[+] Fetching user {} data'.format(args.USERNAME))
	tracks = ml.get_recent_tracks(args.USERNAME, args.NSONGS)

	song_lyrics = download_lyrics(tracks)
	print('[+] Total lyrics downloaded: {}'.format(len(song_lyrics)))

	filter_english(song_lyrics)
	print('[+] Total english lyrics found: {}'.format(len(song_lyrics)))

	emolex = load_emolex(args.LEXICON)
	negative_pct = quantify_negativeness(song_lyrics, emolex)
	print(negative_pct)

	return


main()
