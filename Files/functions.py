import csv
import numpy as np
import ast
import json
import os
import sys
import re
from textblob import TextBlob
import collections
import pandas as pd
import tldextract
import requests
from urllib.parse import urlparse, urlsplit, urlunsplit
from time import sleep

def binaryConversion(outputFile):
    labels = {}
    with open(outputFile, 'r') as f:
        for line in f:
            tweet = json.loads(line)
            if(tweet['mean'] >= 1.9):
                labels[tweet['key']] = 1
            elif(tweet['mean'] <= 1.467):
                labels[tweet['key']] = 0
    return labels
    
def messageFeatureExtraction(tweets, tweet_json, threshold):
    tweetsFeatures = None
    np.array(tweetsFeatures)
    count = 0
    for tweet in tweets:
        print("Starting feature extraction for tweet {} of {}".format(count, len(tweets)))
        indiTweetFeature = []
        #Length of characters 1
        print("Adding Length of charactrs")
        indiTweetFeature.append(len(tweet))
        #print(indiTweetFeature)
        #print(indiTweetFeature)
        
        print("Adding words")
        #Length of words 2
        indiTweetFeature.append(len(tweet.split(" ")))
        #print(indiTweetFeature)
        #print(indiTweetFeature)
        
        print("Adding question mark")
        #Contains question mark 3
        results = collections.Counter(tweet)
        if(results['?'] > 1):
            indiTweetFeature.append(1)
        else:
            indiTweetFeature.append(0)
        #print(indiTweetFeature)
        #print(indiTweetFeature)

        print('Adding exclamation mark')
        #Contains exclamation 4
        if(results['!'] > 1):
            indiTweetFeature.append(1)
        else:
            indiTweetFeature.append(0)
        #print(indiTweetFeature)
        #print(indiTweetFeature)

        print("Adding smiles")
        #Contains emoticon smile 5
        emojis = "😊"
        indiTweetFeature.append(tweet.count(emojis))
        #print(indiTweetFeature)
        #print(indiTweetFeature)

        print("!?")
        #Contains multiple question or exclamation marks 6
        if results['?'] and results['!'] > 1:
            indiTweetFeature.append(1)
        else:
            indiTweetFeature.append(0)
        #print(indiTweetFeature)
        #print(indiTweetFeature)

        print("Adding first person pronouns")
        #Contains pronoun first, sceond, third 7
        first_pronouns = ["i", "we"]
        tweetSplit = tweet.split(" ")
        for x in range(len(tweetSplit)):
            if(tweetSplit[x].lower() in first_pronouns):
                indiTweetFeature.append(1)
                break;
            if(x == len(tweetSplit)-1):
                indiTweetFeature.append(0)
        #print(indiTweetFeature)
        #print(indiTweetFeature)
        print("Adding second person pronouns")
        second_pronouns = ["you"]
        tweetSplit = tweet.split(" ")
        for x in range(len(tweetSplit)):
            if(tweetSplit[x].lower() in second_pronouns):
                indiTweetFeature.append(1)
                break;
            if(x == len(tweetSplit)-1):
                indiTweetFeature.append(0)
        #print(indiTweetFeature)
        #print(indiTweetFeature)
        print("Adding third person pronouns")
        third_pronouns = ["he", "him," "she", "her", "they", "them", "it"]

        tweetSplit = tweet.split(" ")
        for x in range(len(tweetSplit)):
            if(tweetSplit[x].lower() in third_pronouns):
                indiTweetFeature.append(1)
                break;
            if(x == len(tweetSplit)-1):
                indiTweetFeature.append(0)
        #print(indiTweetFeature)
       #print(indiTweetFeature)   
        
        print("Adding uppercase")
        #Count uppercase letters 8
        upperLetterCount = 0
        for letter in tweet:
            if(letter.isupper()):
                upperLetterCount += 1
        indiTweetFeature.append(upperLetterCount)
        #print(indiTweetFeature)
        #print(indiTweetFeature)

        print("Adding url")
        #Number of URLs 9
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] |[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet) 
        indiTweetFeature.append(len(url))
        #print(indiTweetFeature)
        #print(indiTweetFeature)
        
        #Contains popular domain top 100,1000,10000
        print("Adding popular domain")
        file = pd.read_csv('../../Data/top-1m.csv')
        try:
            urls = tweet_json[count]['tweet']['entities']['urls']
        except:
            print(tweet_json[count]['tweet'])
        top100 = 0
        top1000 = 0
        top10000 = 0

        for url in urls:
            urlParsed = None
            rank = None
            try:
                split_url = urlsplit(url['expanded_url'])   
                shortUrl = ''
                if(split_url.netloc[:4] == 'www.'):
                    shortUrl = split_url.netloc[4:]
                else:
                    shortUrl = split_url.netloc
                print(shortUrl)
                print(file.loc[file['site'] == shortUrl]['rank'])
                rank = int(file.loc[file['site'] == split_url.netloc]['rank'])
            except Exception as e:
                rank = 10001
            if rank <= 100:
                top100 = 1
            if rank <= 1000:
                top1000 = 1
            if rank <= 10000:
                top10000 = 1
        
        indiTweetFeature.append(top100)
        indiTweetFeature.append(top1000)
        indiTweetFeature.append(top10000)
                
        print("Adding mention")
        #Contains user mention 10
        result = re.findall("(^|[^@\w])@(\w{1,15})", tweet)
        if(len(result) >= threshold):
            indiTweetFeature.append(1)
        else:
            indiTweetFeature.append(0)
        #print(indiTweetFeature)
        #print(indiTweetFeature)
    
        # Length of hashtags 11
        print("Adding hashtags")
        hashtags = [i  for i in tweet.split() if i.startswith("#") ]
        indiTweetFeature.append(len(hashtags))
        #print(indiTweetFeature)
     
        #Contains stock symbol 12
        print("Addings stocks")
        file = open('../../Data/nasdaqlisted.txt', 'r')
        filecontents = file.readlines()
        stock_symbols = []
        for line in filecontents:
            splitline = line.split("|")
            stock_symbols.append(splitline[0])
            
        del stock_symbols[0]
        
        stockCount = 0
        for word in tweetSplit:
            if(word in stock_symbols):
                stockCount += 1
        
        if(stockCount > 0):
            indiTweetFeature.append(1)
        else:
            indiTweetFeature.append(0)
        #print(indiTweetFeature)
                
        retweets, date = singleMessageFeatureExtraction(tweet_json[count])
        print("Adding retweets")
        indiTweetFeature.append(retweets)
        #print(indiTweetFeature)
        print("Adding date")
        indiTweetFeature = indiTweetFeature + date
        #print(indiTweetFeature)
        
        print("Adding sentiment")
        #Sentiment 13, 14, 15
        positiveWords = 0
        negativeWords= 0
    
    
        tweetSentiment = TextBlob(tweet)
        sentimentScore = tweetSentiment.sentiment[0]
    
        for word in tweetSentiment:
            word = TextBlob(word)
            if(word.sentiment.polarity) > 0:
                positiveWords = positiveWords + 1
            elif(word.sentiment.polarity) < 0:
                negativeWords = negativeWords + 1
        indiTweetFeature.append(positiveWords)
        #print(indiTweetFeature)
        indiTweetFeature.append(negativeWords)
        #print(indiTweetFeature)
        indiTweetFeature.append(sentimentScore)
        #print(indiTweetFeature)
        
        #print(indiTweetFeature)
        indiTweetFeature = [indiTweetFeature]
        if(count == 0):
            #print("hello")
            tweetsFeatures = indiTweetFeature
            #print(tweetsFeatures.shape)
            print("Length of array: {}".format(len(tweetsFeatures[count])))
        else:
            tweetsFeatures = np.append(tweetsFeatures, indiTweetFeature, axis = 0)
            print(tweetsFeatures.shape)
        #print(len(indiTweetFeature))
        print("Finished feature extraction for tweet {} of {}".format(count, len(tweets)))
        count += 1
        
#         if count == 3:
#             break;
    return tweetsFeatures

#TODO: Retweet and date
def singleMessageFeatureExtraction(tweet_json):
    #print(tweet_json)
    retweets = 0
    try:
        retweets = tweet_json["tweet"]["retweet_status"]
        retweets = 1
    except:
        retweets = 0
    date = tweet_json["tweet"]["created_at"].split(" ")[0]
    dates = []
    if date == "Mon":
        dates = [1,0,0,0,0,0,0]
    elif date == "Tue":
        dates = [0,1,0,0,0,0,0]
    elif date == "Wed":
        dates = [0,0,1,0,0,0,0]
    elif date == "Thu":
        dates = [0,0,0,1,0,0,0]
    elif date == "Fri":
        dates = [0,0,0,0,1,0,0]
    elif date == "Sat":
        dates = [0,0,0,0,0,1,0]
    elif date == "Sun":
        dates = [0,0,0,0,0,0,1]
    return retweets, dates