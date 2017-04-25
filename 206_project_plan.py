## Your name: Renee Armstrong
## The option you've chosen: 2

# Put import statements you expect to need here!
import unittest
import re
import ast
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
		CACHE_DICTION[unique_identifier] = omdb_results.text
		f = open(CACHE_FNAME, 'w')
		f.write(str(CACHE_DICTION))
		f.close()

	return omdb_results

## Define a function called get_movie_results which will take one string, the name of the movie
## and return a JSON obj with tweets mentioning that movie, uses caching
def get_movie_tweets(title):
	unique_identifier = "twitter_{}".format(title)
	if unique_identifier in CACHE_DICTION:
		twitter_results = CACHE_DICTION[unique_identifier]		
	else:
		
		twitter_results = t_api.search(title)
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
	movie_info = get_omdb_results(title)
	movie_dicts.append(movie_info)


## Write invocations to the function get_movie_tweets and save those results to a list twitter_info
movie_twitter_info = []
for dict in movie_dicts:
	rdict = json.loads(dict)
	title = rdict["Title"]
	tweets_info = get_movie_tweets(title)
	movie_twitter_info.append((tweets_info,title))


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
cur.execute('CREATE TABLE Users(user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER, num_followers INTEGER)')

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

for movie in movie_dicts:
	rmovie = json.loads(movie)
	imdb_id = rmovie['imdbID']
	title = rmovie['Title']
	director = rmovie['Director']
	num_languages = len(rmovie['Language'].split())
	rating = rmovie['imdbRating']
	actor = rmovie['Actors'].split(',')[0]


	movie_details = (imdb_id, title, director, num_languages, rating, actor)
	cur.execute(statement1, movie_details)



## load into Users table:

statement2 = "INSERT OR IGNORE INTO Users VALUES(?,?,?,?)"

for tweet in movie_twitter_info:
	for status in tweet[0]["statuses"]:
		user_id = status["user"]["id_str"]
		screen_name = status["user"]["screen_name"]
		num_favs = status["user"]["favourites_count"]
		num_followers = status["user"]["followers_count"]

		user_details =(user_id, screen_name, num_favs, num_followers)
		cur.execute(statement2, user_details)

## Load into Tweets Table:
statement3 = "INSERT OR IGNORE INTO Tweets VALUES(?,?,?,?,?,?)"

for tweet in movie_twitter_info:
	title = tweet[1]
	for status in tweet[0]["statuses"]:
		tweet_id = status["id_str"]
		tweet_text = status["text"]
		user_id = status["user"]["id_str"]
		num_retweets = status["retweet_count"]
		num_favs = status["favorite_count"]

		tweet_details = (tweet_id, tweet_text, user_id, title, num_retweets, num_favs)
		cur.execute(statement3, tweet_details)

## Task 3: Create a Class Movie
## Define class movie that accepts a dictionary representative of a movie into the constructor
class Movie:
	def __init__(self, movie_dict):
		
		self.full_results = json.loads(movie_dict)
		self.movie_title = self.full_results["Title"]
		self.director = self.full_results["Director"]
		self.rating = self.full_results["imdbRating"]
		self.actors = self.full_results["Actors"]
		self.languages = self.full_results["Language"]
## Define method that returns the number of languages spoken in the movie
	def num_lang(self):
		return len(self.full_results["Language"].split())
## Define a __str__ method
	def __str__(self):
		return 'Movie Summary\nTitle: {}\nDirector: {}\nRating: {}\nActors: {}\nLanguages: {}\n'.format(self.movie_title, self.director, self.rating, self.actors, self.languages)
## Define a method that returns the string summary
	def pretty(self):
		return 'Movie Summary\nTitle: {}\nDirector: {}\nRating: {}\nActors: {}\nLanguages: {}\n\n'.format(self.movie_title, self.director, self.rating, self.actors, self.languages)


	

## Task 4: Process data from Database tables

## Get all text from tweets

q1 = "SELECT tweet_text FROM Tweets"
cur.execute(q1)
all_tweets = cur.fetchall()


## Use list comphrehension to extract the strings of tweets from the tuples and add them to the list tweet_list
tweet_list = [set[0] for set in all_tweets]

tweet_words = []
for t in tweet_list:
	w = t.split()
	for c in w:
		tweet_words.append(c)


## Use a regular expression to find all hashtags in the tweets and append those to a list tweet_hashtags
tweet_hashtags = []
for tweet in tweet_list:
	hashtags = re.findall(r"#\w*", tweet)
	tweet_hashtags.append(hashtags)

## extract all the hashtags to a list all_hashtags
all_hashtags = []
for tweet in tweet_hashtags:
	for tag in tweet:
		if tag != []:
			all_hashtags.append(tag)




## User a counter to find the most common word among the tweets and save it to the variable most_common
common_words = collections.Counter(tweet_words).most_common()
most_common = common_words[0][0]


## Get the users with followers over 200 and that user's screenname as well as their tweets and save that info to pop_user_tweets
q2 = "SELECT num_followers, screen_name, tweet_text FROM Users INNER JOIN Tweets WHERE num_followers > 200"
cur.execute(q2)
pop_user_tweets = cur.fetchall()

## Sort this info (with lambda function) to find who the user with the highest follower count is and save this to most_pop_user
sorted_user_tweets = sorted(pop_user_tweets, key=lambda x:[0])
most_pop_user = pop_user_tweets[0][1]


## Find out who the director of the movie with the highest IMDB rating is and save that info to pop_director
q3 = "SELECT director FROM Movies ORDER BY rating LIMIT 1"
cur.execute(q3)
pop_director_result = cur.fetchall()
pop_director = pop_director_result[0][0]


## Task 5: Writing a summary to a file summary.text
f = open("summary", "w")
f.write("~~Summary of Test Movies~~\n")

## Create instances of class Movie and write them to the file
for movie in movie_dicts:
	film = Movie(movie)
	f.write(film.pretty())

f.write("\nPopularity Stats:\nUser with most followers: {}\nDirector of Highest Rated Movie: {}\nMost Tweeted Word: {}\n".format(most_pop_user, pop_director, most_common))
f.write("Summary Stats:\nAll Hashtags Tweeted:")
for hashtag in all_hashtags:
	f.write("{}  ".format(hashtag)













##CLOSE YOUR DATABASE CONNECTION
conn.commit()
conn.close()
# Write your test cases here.
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")

class Test(unittest.TestCase):
	def test_caching(self):
		ndirect = open("SI206_final_cache.json","r").read()
		self.assertTrue("Rob Reiner" in ndirect)
		
	def test_users_3(self):
		conn = sqlite3.connect('SI206_finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=3, "Testing there are at least 3 records in the Users database")
		conn.close()
	def test_movies_3(self):
		conn = sqlite3.connect('SI206_finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies')
		result = cur.fetchall()
		self.assertTrue(len(result)>=3)
		conn.close()
	def test_movies_col(self):
		conn = sqlite3.connect('SI206_finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Movies table")
		conn.close()
	def test_users_col(self):
		conn = sqlite3.connect('SI206_finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==4,"Testing that there are 4 columns in the Users table")
		conn.close()
	def test_tweets_col(self):
		conn = sqlite3.connect('SI206_finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
		conn.close()


## Remember to invoke all your tests...
if __name__ == "__main__":
	unittest.main(verbosity=2)