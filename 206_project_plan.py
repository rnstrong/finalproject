## Your name: Renee Armstrong
## The option you've chosen: 2

# Put import statements you expect to need here!
import unittest
import requests
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

# Set up library to grab stuff from twitter with authentication, and return it in a JSON format 
t_api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

# Set up list to grab stuff from the OMDB API 
test_titles = ["Princess Bride", "Avengers", "The Fifth Element"]



## Task 1 - Getting Data 
## Define a function called get_omdb_results which will take one string, the title of a movie
## and will return a JSON object of information from OMDB about that movie and uses caching
def get_omdb_results(title):
	unique_identifier = "omdb_{}".format(title)
	if unique_identifier in CACHE_DICTION:
		omdb_results = CACHE_DICTION[unique_identifier]		
	else:
		d = {'t': title}
		omdb_results = requests.get("http://www.omdbapi.com/", params=d)
		CACHE_DICTION[unique_identifier] = omdb_results
		f = open(CACHE_FNAME, 'w')
		f.write(str(CACHE_DICTION))
		f.close()

	return omdb_results

## Define a function called get_twitter_results which will take one string, either the name of the actor
## or director for a particular movie, and return a JSON obj with information about that user and uses caching
def get_user_info(username):
	unique_identifier = "twitter_{}".format(username)
	if unique_identifier in CACHE_DICTION:
		twitter_results = CACHE_DICTION[unique_identifier]		
	else:
		
		twitter_results = t_api.user_timeline(username)
		CACHE_DICTION[unique_identifier] = twitter_results
		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	return twitter_results


## Set up caching dict here
CACHE_FNAME = "SI206_final_cache.json"
try: 
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read()
	CACHE_DICTION = json.loads(cache_contents)
	cache_file.close()
except:
	CACHE_DICTION = {}


## Write invocations to the function get_omdb_results and save those results to a list movie_dicts
movie_dicts = []

for title in test_titles:
	movie_info = get_omdb_results(title).text
	movie_dicts.append(movie_info)


## Write invocations to the function get_user_results and save those results to a list twitter_info
director_twitter_info = []
#for dict in movie_dicts:
	#director = dict["Director"]
	#user_info = get_user_results(director)
	#twitter_info.append(user_info)


## Task 2 - Creating database and loading data into database
## Create a database file 'SI206_finalproject.db' with 3 tables (tweets, users, movies)
## The Tweets table should hold in each row:
##Tweet text
##Tweet ID (primary key)
##The user who posted the tweet (represented by a reference to the users table)
##The movie search this tweet came from (represented by a reference to the movies table)
##Number favorites
##Number retweets

conn = sqlite3.connect('SI206_finalproject.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Tweets')
cur.execute('CREATE TABLE Tweets(tweet_id TEXT PRIMARY KEY, tweet_text TEXT, user_id TEXT, title TEXT, num_retweets INTEGER, num_favorites)')



## The Users table should hold in each row:
##screen name text
##User ID (primary key)
##The user who posted the tweet (represented by a reference to the users table)
##The movie search this tweet came from (represented by a reference to the movies table)
##Number favorites
##Number retweets


cur.execute('DROP TABLE IF EXISTS Users')
cur.execute('CREATE TABLE Users(user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER, num_followers TEXT)')

## The Movies table should hold in each row:
#ID (primary key) (NOTE title is dangerous for a primary key, 2 movies could have the same title!)
#Title of the movie
#Director of the movie 
#Number of languages the movie has
#IMDB rating of the movie
#The top billed (first in the list) actor in the movie


cur.execute('DROP TABLE IF EXISTS Movies')
cur.execute('CREATE TABLE Movies(imdb_id TEXT PRIMARY KEY, title TEXT, director TEXT, num_languages INTEGER, rating INTEGER, actor TEXT)')

## load into the Movies table:

statement1 = "INSERT OR IGNORE INTO Movies VALUES(?,?,?,?,?,?)"
#for movie in movie_dicts:
	#imdb_id = movie['imdbID']
	#title = movie['Title']
	#director = movie['Director']
	#num_languages = len(movie['Language'].split())
	#rating = movie['imdbRating']
	#actor = movie['Actors'].split(',')[0]


	#movie_details = (imdb_id, title, director, num_languages, rating, actor)
	#cur.execute(statement1, movie_details)





##CLOSE YOUR DATABASE CONNECTION
conn.commit()
conn.close()
# Write your test cases here.
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")

class Test(unittest.TestCase):
	def test_caching(self):
		ndirect = open("final_project_cache.json","r").read()
		self.assertTrue("Rob Reiner" in ndirect)
	def test_users_3(self):
		conn = sqlite3.connect('SI206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=3, "Testing there are at least 3 records in the Users database")
		conn.close()
	def test_movies_3(self):
		conn = sqlite3.connect('SI206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies')
		result = cur.fetchall()
		self.assertTrue(len(result)>=3)
		conn.close()
	def test_movies_col(self):
		conn = sqlite3.connect('SI206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Movies table")
		conn.close()
	def test_users_col(self):
		conn = sqlite3.connect('SI206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==4,"Testing that there are 4 columns in the Users table")
		conn.close()
	def test_tweets_col(self):
		conn = sqlite3.connect('SI206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
		conn.close()


## Remember to invoke all your tests...
if __name__ == "__main__":
	unittest.main(verbosity=2)