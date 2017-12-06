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
from subprocess import call

API_KEY = 'c9a7f0509e1be9ea5e8b1fce88bd1486'
API_SECRET = '93de978ac877b9c01079ce0cd32ae4ec'


negative_emotions = [
	'anger', 'disgust', 'fear', 'negative', 'sadness'
]

unwanted_pos_tags = [
	'CC', 'CD', 'DT', 'IN', 'PRP', 'TO', 'NNP', 'PRP$', 'WP', 'WP$', 'EX',
	'LS', 'POS', 'UH', 'WDT', 'WP', 'WRB'
]


ccm = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=ccm)

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

	parser.add_argument('--p', help='Enable plot generation',
		action='store_true')

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
		title = artist + ' - ' + song

		try:
			if title not in song_lyrics:
				lyrics = lw.get_lyrics(artist, song)

				if len(lyrics.split()) != 1: # Non-instrumental
					song_lyrics[title] = lyrics
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

		len_tokens = len(tokens)
		total_tokens = len_tokens if len_tokens != 0 else 1 
		negative_tokens = 0

		for token in tokens:
			for emotion in negative_emotions:
				if token.lower() in emolex[emotion]:
					negative_tokens += 1
					break

		negative_pct[song] = negative_tokens/total_tokens

	return negative_pct


def plot(songs, track_info):
	plot_file = open('plotcmd.gp', 'w')
	data_file = open('data.dat', 'w')

	# GNUPlot commands
	plot_file.write('set terminal png size 1200, 900\n')
	plot_file.write('set output \'time_nei.png\'\n')
	plot_file.write('set title \'Tempo (canções) x Índice de Negatividade\'\n')
	plot_file.write('set xlabel \'Tempo (canções)\'\n')
	plot_file.write('set ylabel \'Índice de Negatividade\'\n')

	# Data file
	i = 1
	for (artist, song) in reversed(songs):
		title = artist + ' - ' + song
		NeI = track_info[title]['nei']

		if NeI != None:
			data_file.write(str(i) + '\t' + str(NeI) + '\n')
			i += 1

	data_file.close()

	plot_file.write('plot \'data.dat\' u 1:2 notitle smooth bezier')
	plot_file.close()
	call(['gnuplot', 'plotcmd.gp'])


def get_spotify_info(songs, song_lyrics, negative_pct):
	print('[+] Collecting tracks info')
	track_info = {}
	for (artist, song) in songs:
		title = artist + ' - ' + song
		print('\t' + title)

		if title in track_info:
			continue

		search_result = sp.search(title)['tracks']['items']

		if len(search_result) != 0:
			uri = search_result[0]['uri']
			features = sp.audio_features(uri)[0]

			if features:
				duration_ms = features['duration_ms']
				valence = features['valence']
			else:
				valence = None
				duration_ms = 1
		else:
			valence = None
			duration_ms = 1

		if title in song_lyrics:
				lyric_weight = len([x for x in song_lyrics[title].split() \
					if x.isalpha()]) / (duration_ms / 1000)

				lyric_neg = negative_pct[title]
		else:
			lyric_weight = None
			lyric_neg = None

		if valence == None or lyric_neg == None:
			NeI = None
		else:
			NeI = ((1 - valence) + (lyric_neg * lyric_weight)) / 2

		track_info[title] = {
			'lyric_weight': lyric_weight, 'valence': valence,
			'lyric_neg': lyric_neg, 'nei': NeI
		}

	return track_info


def main():
	args = add_args()

	# Fetch user lastfm data.
	print('[+] Fetching user {} data'.format(args.USERNAME))

	if args.NSONGS != 0:
		tracks = ml.get_recent_tracks(args.USERNAME, args.NSONGS)
	else:
		tracks = ml.get_recent_tracks(args.USERNAME, None)

	songs = [tuple(str(t.track).split(' - ')[0:2]) for t in tracks]

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
	track_info = get_spotify_info(songs, song_lyrics, negative_pct)

	for (artist, song) in songs:
		title = artist + ' - ' + song
		print(title, track_info[title]['nei'])

	if args.p:
		plot(songs, track_info)

main()
