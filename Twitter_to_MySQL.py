#!usr/bin/python
import json
from dateutil import parser
import mysql.connector
from mysql.connector import Error
import tweepy
import time
import os
import subprocess


consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']
password = os.environ['PASSWORD']


def connect(username, created_at, tweet, retweet_count, place , location):
	"""
	Function to establish database connection
	"""
	try:
		con = mysql.connector.connect(host = 'localhost',
		database='sys', user='root', password = '12345678', charset = 'utf8')
		

		if con.is_connected():
			"""
			Twitter data inserted into table
			"""
			cursor = con.cursor()
			
			query = "INSERT INTO tweets (username, created_at, tweet, retweet_count,place, location) VALUES (%s, %s, %s, %s, %s, %s)"
			cursor.execute(query, (username, created_at, tweet, retweet_count, place, location))
			con.commit()
			
			
	except Error as e:
		print(e)

	return



class Streamlistener(tweepy.StreamListener):
	

	def on_connect(self):
		print("Connected to Twitter API")


	def on_error(self):
		if status_code != 200:
			print("error found")
			# returning false disconnects the stream
			return False

	"""
	Json data is extracted to read the data needed
	"""
	def on_data(self,data):
		
		try:
			raw_data = json.loads(data)

			if 'text' in raw_data:
				 
				username = raw_data['user']['screen_name']
				created_at = parser.parse(raw_data['created_at'])
				tweet = raw_data['text']
				retweet_count = raw_data['retweet_count']

				if raw_data['place'] is not None:
					place = raw_data['place']['country']
					print(place)
				else:
					place = None
				

				location = raw_data['user']['location']

				#data streamed into database
				connect(username, created_at, tweet, retweet_count, place, location)
				print("Tweet retrieved at: {} ".format(str(created_at)))
		except Error as e:
			print(e)


if __name__== '__main__':



	# authentification so we can access twitter
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api =tweepy.API(auth, wait_on_rate_limit=True)

	# create instance of Streamlistener
	listener = Streamlistener(api = api)
	stream = tweepy.Stream(auth, listener = listener)

	track = ['Avengers', 'Marvel Movies', 'MCU', 'Iron Man', 'Thor']
	stream.filter(track = track, languages = ['en'])

