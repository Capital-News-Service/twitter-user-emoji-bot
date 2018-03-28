import tweepy as tweepy
import requests as requests
import json
import re

keys={}
with open("/Users/jagluck/Documents/GitHub/twitter-user-emoji-bot/keys.json","r") as f:
    keys = json.loads(f.read())
    
# Consumer keys and access tokens, used for OAuth
consumer_key = keys["consumer_key"]
consumer_secret = keys["consumer_secret"]
access_token = keys["access_token"]
access_token_secret = keys["access_token_secret"]

emojis={}
with open("/Users/jagluck/Documents/GitHub/twitter-user-emoji-bot/emojis.json","r") as f:
    emojis = json.loads(f.read())

 
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)

def sendTweet(content):
    api.update_status(content)
    
def buildTweet(text, link):
    tweet = text + " " + link
    sendTweet(tweet)

def translateText(text):
	words = re.split("\W+",text)

	# for word in words: 
	# 	for emoji, keywords in emojis.items():
	# 		for title, keywordlist in keywords:
	# 			print(keywordlist)
	# 			print("-----")
	# 			if word in keywordlist:
	# 				text = text.replace(word, "replaced")

	for word in words:
		for emojiName, emojiInfo in emojis.items():
			if word in emojiInfo['keywords']:
				text = text.replace(word, "replaced")

	print(text)

def getCurrentTweets():
	tweets = api.user_timeline(screen_name = 'realDonaldTrump', count = 50, include_rts = False)
	for x in tweets:
		tweet = x._json
		text = tweet['text']
		translated = translateText(text)
		print(translated)
		print("---------")

getCurrentTweets()
#translateText("scream up down happy ghhghghg sad")