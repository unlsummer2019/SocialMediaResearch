import json
import tweepy
import sys
import pprint
import os
import ConfigParser
import time
def send(tweetid):
	
	# Access the tweepy API
	config = ConfigParser.ConfigParser()
	config.read('twitter.ini')
	consumer_key = config.get('Twitter', 'consumer_key')
	consumer_secret = config.get('Twitter', 'consumer_secret')
	access_key = config.get('Twitter', 'access_key')
	access_secret = config.get('Twitter', 'access_secret')
	auth = tweepy.OAuthHandler("z7d23cQWW3IE9IMFOV5DwjDzm", "COUn7QLcCDUj8ct8DLxY9kEjcfkOC3FNqXEr9q0x8hmOhyZrJE")
	auth.set_access_token("941707847238373376-R4517e2MlbF1T3kGSOnRJmA2ay0MGZy","wBQklX4XgWaLGXRw7kWW9mxSpAA4wyQF1VIdHnXzP94WF")
	api = tweepy.API(auth)

	tweet = api.get_status(tweetid)

	# Gets the tweet and sends it to get.thread.php
	try:
		tweet = api.get_status(tweetid)
		print json.dumps(tweet.json)
	except:
		sys.exit()

if __name__ == '__main__':
	tweetid = sys.argv[1]
	send(tweetid)
