#!/usr/bin/env python3

'''
Moodic
@author: Hugo Sousa
'''

import argparse
import lyricwikia as lw
import mylast as ml
import pylast
import spotipy
import sys

from langdetect import detect
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from tqdm import tqdm
from spotipy.oauth2 import SpotifyClientCredentials

API_KEY = 'c9a7f0509e1be9ea5e8b1fce88bd1486'
API_SECRET = '93de978ac877b9c01079ce0cd32ae4ec'


negative_emotions = [
	'anger', 'disgust', 'fear', 'negative', 'sadness'
]

unwanted_pos_tags = [
	'CC', 'CD', 'DT', 'IN', 'PRP', 'TO', 'NNP', 'PRP$', 'WP', 'WP$', 'EX',
	'LS', 'POS', 'UH', 'WDT', 'WP', 'WRB'
]


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
	english_lyrics = {}
	for song in song_lyrics:
		language = detect(song_lyrics[song])
		if language == 'en':
			english_lyrics[song] = song_lyrics[song]

	return english_lyrics


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


def quantify_negativity(lyrics, emolex):
	wnl = WordNetLemmatizer()

	negative_pct = {}
	stop_words = set(stopwords.words('english'))

	print('[+] Calculating lyrics negativity')
	for song in lyrics:
		tokens = [t for t in word_tokenize(lyrics[song]) \
			if t not in stop_words and t.isalpha()]
		tokens = set([wnl.lemmatize(t) for t in tokens])
		tagged = pos_tag(tokens)
		tokens = [x[0] for x in tagged if x[1] not in unwanted_pos_tags]

		total_tokens = len(tokens)
		negative_tokens = 0

		for token in tokens:
			for emotion in negative_emotions:
				if token.lower() in emolex[emotion]:
					negative_tokens += 1
					break

		negative_pct[song] = negative_tokens/total_tokens

	return negative_pct


def main():
	args = add_args()

	# Fetch user lastfm data.
	print('[+] Fetching user {} data'.format(args.USERNAME))
	tracks = ml.get_recent_tracks(args.USERNAME, args.NSONGS)

	# Downlaod lyrics
	song_lyrics = download_lyrics(tracks)
	print('[+] Total lyrics downloaded: {}'.format(len(song_lyrics)))

	# Remove non english songs
	song_lyrics = filter_english(song_lyrics)
	print('[+] Total english lyrics found: {}'.format(len(song_lyrics)))

	# Load Word-emotion lexicon and calculate negativity
	emolex = load_emolex(args.LEXICON)
	negative_pct = quantify_negativity(song_lyrics, emolex)
	
	# Get Spotify info
	ccm = SpotifyClientCredentials()
	sp = spotipy.Spotify(client_credentials_manager=ccm)
	result = sp.search('The Smiths - Asleep')

	print('[+] Collecting tracks info')
	track_info = {}
	for song in song_lyrics:
		uri = sp.search(song)['tracks']['items'][0]['uri']
		features = sp.audio_features(uri)[0]
		duration_ms = features['duration_ms']
		valence = features['valence']

		track_info[song] = {'uri': uri, 'length': duration_ms,
			'valence': valence, 'lyric_neg': negative_pct[song]}

	for track in track_info:
		print(track, track_info[track])

main()
