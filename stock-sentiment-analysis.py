import sys, tweepy, json, pprint
from tweepy import OAuthHandler
from watson_developer_cloud import ToneAnalyzerV3

consumer_key = "CDp27QMWoja85UyiXTBOiyojQ"
consumer_secret = "VNaCDxJ4jCrpGxIfcZW5LfwkIvZsbDNFVeD3BowupOVsfzcXgC"
access_token = "800219735820410881-5GXTphkqqlk6M2Y3KvV4AeaCaDn3YyL"
access_secret = "c7sFYQmKWpmr7NuFb9g9clfr22Kqdn9ud96ZqpFWvxuHk"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)
tone_analyzer = ToneAnalyzerV3(
  version="2017-08-02",
  username="dd9ba104-19cf-4592-b7aa-623df89b0fd7",
  password="QSqPq6AsLvXo"
)

lastId = -1

def collectTweets(symbol, tweetCount):
    global lastId
    symbol = "$" + symbol
    print "Getting", tweetCount, "tweets regarding", symbol
    fileName = symbol + ".txt"
    tweetsCollected = 0
    tweetsToCollect = int(tweetCount)
    with open(fileName, "w") as f:
        while tweetsCollected < tweetsToCollect:
            try:
                if lastId <= 0:
                    newTweets = api.search(q=symbol, count=100)
                else:
                    newTweets = api.search(q=symbol, count=100, max_id=str(lastId-1))
                if not newTweets:
                    print("No more tweets")
                    break
                for tweet in newTweets:
                    tweetText = tweet._json["text"]
                    cleanText = ''.join([i if ord(i) < 128 else '' for i in tweetText])
                    f.write(cleanText + "\n")
                tweetsCollected += len(newTweets)
                lastId = newTweets[-1].id
            except tweepy.TweepError as e:
                print(e)
                break
    f.close()
    print "Collected", tweetsCollected ,"tweets"
    return

def sentimentAnalysis(symbol):
    fileName = "$" + symbol + ".txt"
    text_corpus = ''
    with open(fileName, "r") as f:
        for line in f:
            text_corpus += line
        tone = tone_analyzer.tone(text = text_corpus, tones="emotion", content_type="text/plain", sentences = False)
        tones = tone["document_tone"]["tone_categories"][0]["tones"]
        joy = [x for x in tones if x["tone_name"] == "Joy"]
        return joy[0]["score"]

if __name__ == "__main__":
    try:
        collectTweets(sys.argv[1], sys.argv[2])
        polarity = sentimentAnalysis(sys.argv[1])
        if polarity > .50:
            print "People are generally positive about $" + sys.argv[1] + " with a polarity of " + str(polarity)
    except IndexError:
        print "Error: Missing parameters. \nExample parameters: $SHOP 1000"
