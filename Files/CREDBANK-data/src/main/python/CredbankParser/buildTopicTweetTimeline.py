#!/usr/bin/python

# Given a file in the format of cred_event_SearchTweets.data,
# find the topic key, terms, count, and tweet data. Then output
# the topic ID, term count, and list of tweet IDs.

import json
import sys
import re

idRegEx = re.compile(r".*ID=")
endElRegEx = re.compile(r"'.*")

inputFile = sys.argv[1]
outputFile = sys.argv[2]

output = open(outputFile, "w")

with open(inputFile, "r") as f:
    header = f.next()

    for line in f:
        topicData = line.split("\t")

        topicKey = topicData[0]
        topicTerms = topicData[1]
        topicTweetCount = topicData[2]
        tweetIdList = topicData[3]

        print topicKey

        realTweetIds = []

        # Need to read: [('ID=522759240817971202', 'AUTHOR=i_Celeb_Gossips', 'CreatedAt=2014-10-16 14:41:30'),...]
        idElements = tweetIdList.split("),")
        for element in idElements:
            elArr = element.split(",")
            idEl = filter(lambda x: "ID" in x, elArr)[0]
            idEl = idRegEx.sub("", idEl)
            idEl = endElRegEx.sub("", idEl)

            realTweetIds.append(long(idEl))

        realTweetIds = list(set(realTweetIds))

        topicMap = {
            "key" : topicKey,
            "terms" : topicTerms.split(","),
            "count" : topicTweetCount,
            "tweets" : realTweetIds
        }

        json.dump(topicMap, output, sort_keys=True)
        output.write("\n")

output.close()