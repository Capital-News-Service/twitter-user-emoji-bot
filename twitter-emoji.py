import boto
import boto.s3.connection
import boto3
import tweepy as tweepy
import requests as requests
import json
import re
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

keys={}
with open("/Users/jagluck/Documents/GitHub/twitter-user-emoji-bot/keys.json","r") as f:
    keys = json.loads(f.read())
    
# Consumer keys and access tokens, used for OAuth
tw_consumer_key = keys["tw_consumer_key"]
tw_consumer_secret = keys["tw_consumer_secret"]
tw_access_token = keys["tw_access_token"]
tw_access_token_secret = keys["tw_access_token_secret"]
db_access_key = keys["db_access_key"]
db_secret_key = keys["db_secret_key"]

bucket_name = 'trump-last-tweets' # replace with your bucket name
object_key = 'tweets.json' # replace with your object key

emojis={}
with open("/Users/jagluck/Documents/GitHub/twitter-user-emoji-bot/emojis.json","r") as f:
    emojis = json.loads(f.read())

 
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(tw_consumer_key, tw_consumer_secret)
auth.set_access_token(tw_access_token, tw_access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)

s3 = boto3.resource('s3',
         aws_access_key_id=db_access_key,
         aws_secret_access_key=db_secret_key)
my_bucket = s3.Bucket(bucket_name)

def sendTweet(content):
    api.update_status(content)
    
def buildTweet(text, link):
    tweet = text + " " + link
    sendTweet(tweet)
	

def readDatabase():

	with open('tweets.json','wb') as data:
		my_bucket.download_fileobj(object_key, data)

	old_tweets={}
	with open("/Users/jagluck/Documents/GitHub/twitter-user-emoji-bot/tweets.json","r") as f:
	    text = f.read()
    
	old_tweets = json.loads(text)
	return old_tweets['tweets']

def updateDatabase(json_data):

	with open('tweets.json', 'wb') as outfile:
		outfile.write(json_data)

	with open('tweets.json', 'rb') as data:
		my_bucket.upload_fileobj(data, object_key)


def translateText(text):
	text = re.sub(r'https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
	words = re.split("\W+",text)

	print(text)
	new_text = ''
	for word in words:
		new_word = ''
		if word not in stopwords.words('english'):
			new_word = getTopEmoji(word)

		new_text = new_text + new_word

	return(new_text)

def getTopEmoji(word):
	raw = requests.get("https://emojipedia.org/search/?q=" + word)
	soup = BeautifulSoup(raw.text, "lxml")
	result = soup.find("ol", {"class": "search-results"})

	new_word = ''
	if (result):
		results = result.findAll('li')

		max = 0

		emoj = results[0].find('span').text
		des = results[0].find('p').text
		if des != "😞 No results found. Perhaps try a less specific search phrase.":
			new_word = emoj
		
	return new_word

def getMatchEmoji(word, text):
	raw = requests.get("https://emojipedia.org/search/?q=" + word)
	soup = BeautifulSoup(raw.text, "lxml")
	result = soup.find("ol", {"class": "search-results"})

	new_word = ''
	if (result):
		results = result.findAll('li')
		des = results[0].find('p').text
		max = -1

		if des != "😞 No results found. Perhaps try a less specific search phrase.":
			for res in results:
				sp = res.find('span')
				emoj = sp.text
				des = res.find('p').text
				if des != "😞 No results found. Perhaps try a less specific search phrase.":
					des = des.replace("…", "")
					des = des.replace(",", "")
					des = des.replace(".", "")
					des = des.replace("(", "")
					des = des.replace(")", "")
					des = des.replace("A ", "")
					des = des.split(" ")
					des = [word for word in des if word not in stopwords.words('english')]
					des = ' '.join(des)
					counter = -1
					for x in text:
					    if x in des:
					        counter += 1

					if counter > max:
						max = counter
						new_word = emoj

	return new_word

def getCurrentTweets():
	tweets = api.user_timeline(screen_name = 'realDonaldTrump', count = 50, include_rts = False, tweet_mode='extended')
	
	found_tweets = []
	found_links = {}

	for x in tweets:
		tweet = x._json
		text = tweet['full_text']
		found_tweets.append(text)
		link = tweet['id']
		found_links[text] = link
	data = {}
	data['tweets'] = found_tweets
	data['links'] = found_links
	return(data) 

def runBot():
	old_tweets = readDatabase()
	current = getCurrentTweets()
	new_tweets = current['tweets']
	links = current['links']

	for new in new_tweets:
		if new not in old_tweets:
			translated = translateText(new)
			tweet_id = links[new]
			sendTweet(translated + " " + "https://twitter.com/realDonaldTrump/status/" + str(tweet_id))

	json_data = json.dumps(new_tweets)
	#updateDatabase(json_data.encode('utf-8'))


runBot()