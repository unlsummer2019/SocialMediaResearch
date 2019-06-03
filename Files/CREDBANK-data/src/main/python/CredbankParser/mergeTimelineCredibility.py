#!/usr/bin/python

# Given a file in the format of cred_event_TurkRatings.data
# and a file from buildTopicTweetTimeline.py, merge the two 
# files to create a single file with both ratings and tweet
# IDs

import numpy as np
import json
import sys
import re

idRegEx = re.compile(r".*ID=")
endElRegEx = re.compile(r"'.*")

ratingsFile = sys.argv[1]
tweetsFile = sys.argv[2]
outputFile = sys.argv[3]

tweetsMap = {}
with open(tweetsFile, "r") as f:

    for line in f:
        tweetData = json.loads(line)
        tweetsMap[tweetData["key"]] = tweetData

output = open(outputFile, "w")

with open(ratingsFile, "r") as f:
    header = f.next()

    for line in f:
        topicData = line.split("\t")

        topicKey = topicData[0]
        topicTerms = topicData[1]
        ratings = topicData[2]
        reasons = topicData[3]

        ratings = map(lambda x: int(x.strip().replace("'", "")), ratings.replace("[", "").replace("]", "").split(","))
        ratings = np.array(ratings)

        tweetsMap[topicKey]["ratings"] = ratings.tolist()
        tweetsMap[topicKey]["mean"] = ratings.mean()

        topicMap = tweetsMap[topicKey]

        print topicMap["key"], topicMap["mean"]

        json.dump(topicMap, output, sort_keys=True)
        output.write("\n")

output.close()