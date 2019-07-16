import re
import pandas as pd 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import nltk
import matplotlib.pyplot as plt
from textblob import TextBlob
import time
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import mysql.connector 
from mysql.connector import Error
import os
from wordcloud import WordCloud, STOPWORDS
import numpy as np



def removal_of_non_ascii(tweet):
		return ''.join(i for i in tweet if ord(i)<128)

class TweetObject():


	def __init__(self, host, database, user):
		self.password = '12345678'
		self.host = host
		self.database = database
		self.user = user

 


	def MySQLConnect(self,query):
		"""
		Connects to database and extracts
		raw tweets and any other columns
		needed
		Parameters:
	
		"""

		try:
			con = mysql.connector.connect(host = 'localhost',
		database='sys', user='root', password = '12345678', charset = 'utf8')

			if con.is_connected():
				print("Success: connected to database")

				cursor = con.cursor()
				query = query
				cursor.execute(query)

				data = cursor.fetchall()
				# code to store data in dataframe
				df = pd.DataFrame(data,columns = ['date', 'tweet'])
				df['tweet'] = df['tweet'].apply(removal_of_non_ascii)	




		except Error as e:
			print(e)
		
		cursor.close()
		con.close()

		return df


	def cleaning_the_tweets(self, df):
	
		"""
		Preprocessing raw
		"""

		#text preprocessing
		stopword_list = stopwords.words('english')
		ps = PorterStemmer()
		df["cleaning_the_tweets"] = None
		df['len'] = None
		for i in range(0,len(df['tweet'])):
			# removal on non symbols

			list_exclusion = ['[^a-zA-Z]','rt', 'http', 'co', 'RT']
			exclusions = '|'.join(list_exclusion)
			text = re.sub(exclusions, ' ' , df['tweet'][i])
			text=text.encode('ascii', 'ignore').decode('ascii')
			text = text.lower()
			words = text.split()
			words = [word for word in words if not word in stopword_list]
			df['cleaning_the_tweets'][i] = ' '.join(words)


		# Create column with data length
		df['len'] = np.array([len(tweet) for tweet in data["cleaning_the_tweets"]])
			


		return df


	def text_blob(self, tweet):
		"""
		This definiton is used to calculate sentiment analysi using textblob
		----------------
		arg1: takes in a tweet (row of dataframe)
		"""

		# need to improce
		analysis = TextBlob(tweet)
		if analysis.sentiment.polarity > 0:
			return 1
		elif analysis.sentiment.polarity == 0:
			return 0
		else:
			return -1

    #Vader Implementation
	def vader(self,tweet):
		sid = SentimentIntensityAnalyzer()
		ss = sid.polarity_scores(tweet)
		if (ss['compound'] > 0.05):
			return 1
				#print ("pos")
		elif (ss['compound'] > -0.05 and ss['compound'] < 0.05):
			return 0
				#print ("neu")
		else :
				#print ("neg")
			return -1
			
	def save_to_csv(self, df):
		"""
		save data into CSV file
		"""
		try:
			df.to_csv("cleaning_the_tweets.csv")
			print("\n")
			print("csv successfully saved. \n")

		
		except Error as e:
			print(e)
		



	def word_cloud(self, df):
		plt.subplots(figsize = (12,10))
		wordcloud = WordCloud(
				background_color = 'white',
				width = 1000,
				height = 800).generate(" ".join(df['cleaning_the_tweets']))
		plt.imshow(wordcloud)
		plt.axis('off')
		plt.show()





if __name__ == '__main__':

	t = TweetObject( host = 'localhost', database = 'sys', user = 'root')

	data  = t.MySQLConnect("SELECT created_at, tweet FROM `sys`.`tweets`;")
	data = t.cleaning_the_tweets(data)
	start_textblob = time.time()
	data['Textblob'] = np.array([t.text_blob(x) for x in data['cleaning_the_tweets']])
	end_textblob = time.time()
	start_vader = time.time()
	data['Vader'] = np.array([t.vader(x) for x in data['cleaning_the_tweets']])
	end_vader = time.time()
	#t.word_cloud(data)
	t.save_to_csv(data)
	
	pos_tweets = [tweet for index, tweet in enumerate(data["cleaning_the_tweets"]) if data["Textblob"][index] > 0]
	neg_tweets = [tweet for index, tweet in enumerate(data["cleaning_the_tweets"]) if data["Textblob"][index] < 0]
	neu_tweets = [tweet for index, tweet in enumerate(data["cleaning_the_tweets"]) if data["Textblob"][index] == 0]
	
	print ("Textblob results:")
	
	print("percentage of positive tweets: {}%".format(100*(float(len(pos_tweets))/float(len(data['cleaning_the_tweets'])))))
	print("percentage of negative tweets: {}%".format(100*(float(len(neg_tweets))/float(len(data['cleaning_the_tweets'])))))
	print("percentage of neutral tweets: {}%".format(100*(float(len(neu_tweets))/float(len(data['cleaning_the_tweets'])))))
	# print ("Runtime for Textblob: ")
	# print (end_textblob-start_textblob)
	
	# pos_tweets2 = [tweet for index, tweet in enumerate(data["cleaning_the_tweets"]) if data["Vader"][index] > 0]
	# neg_tweets2 = [tweet for index, tweet in enumerate(data["cleaning_the_tweets"]) if data["Vader"][index] < 0]
	# neu_tweets2 = [tweet for index, tweet in enumerate(data["cleaning_the_tweets"]) if data["Vader"][index] == 0]
	
	# print ("Vader results:")
	
	# print("percentage of positive tweets: {}%".format(100*(float(len(pos_tweets2))/float(len(data['cleaning_the_tweets'])))))
	# print("percentage of negative tweets: {}%".format(100*(float(len(neg_tweets2))/float(len(data['cleaning_the_tweets'])))))
	# print("percentage of neutral tweets: {}%".format(100*(float(len(neu_tweets2))/float(len(data['cleaning_the_tweets'])))))
	# print ("Runtime for Vader: ")
	# print (end_vader-start_vader)
	
	
	
