Fetch all tweets (or statuses) for a Twitter user, 200 at a time, and save them in a
local MongoDB database named "tweets" inside the "statuses" collection.

WARNING: This script doesn't care about your API rate limits, it fetches as many as
possible as quickly as possible. Use at your own risk! You may be temporarily or
permanently blocked by Twitter. Edit TWITTER_USERNAME and TWITTER_PASSWORD at the
top of the source code with your username and password to use higher limits.

Requirements:

    - Python (tested on 2.6)
    - python-twitter
    - pymongo

Sample usage:

    Fetch all tweets, starting from current, working backward to the first tweet:
    $ python gettweets.py -u ev

    Fetch all tweets newer than the latest one in the database:
    $ python gettweets.py -u ev -n

    Fetch other user's tweets:
    $ python gettweets.py -u biz

Do whatever with the database:

    $ python
    >>> import pymongo
    >>> statuses = pymongo.Connection().tweets.statuses
    >>> statuses.count()
    >>> statuses.create_index("text")
    >>> evs_tweets = statuses.find({'user': 'ev'})
    >>> evs_latest_tweet = evs_tweets.sort("created_at", pymongo.DESCENDING)[0]
    >>> evs_earliest_tweet = evs_tweets.sort("created_at", pymongo.ASCENDING)[0]
    >>> bizs_first_tweet = statuses.find({'user': 'biz'}).sort("created_at", pymongo.ASCENDING)[0]

Notes:
- I got bored and fed up with the Twitter's lack of ability to properly search my own tweets
- I wanted to play around with MongoDB
- It's probably lame, definitely simplistic, and plenty of hardcoded stuff
- Feel free to use and improve

-- 
Ronny Haryanto