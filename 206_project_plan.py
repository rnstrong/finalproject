## Your name: Renee Armstrong
## The option you've chosen: 2

# Put import statements you expect to need here!
import unittest
import tweepy
import twitter_info
import json
import sqlite3
import itertools
import collections
##if you're on windows:
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)



##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)














# Write your test cases here.
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")

class Test(unittest.TestCase):
	def test_caching(self):
		ndirect = open("final_project_cache.json","r").read()
		self.assertTrue("Rob Reiner" in ndirect)
	def test_users_3(self):
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=3, "Testing there are at least 3 records in the Users database")
		conn.close()
	def test_movies_3(self):
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies')
		result = cur.fetchall()
		self.assertTrue(len(result)>=3)
		conn.close()
	def test_movies_col(self):
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Movies table")
		conn.close()
	def test_users_col(self):
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==4,"Testing that there are 4 columns in the Users table")
		conn.close()
	def test_tweets_col(self):
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
		conn.close()


## Remember to invoke all your tests...
if __name__ == "__main__":
	unittest.main(verbosity=2)