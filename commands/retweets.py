import discord
from catch.catch_tweets import client
import tweepy
import csv
from io import StringIO
import re
PROFILE_BASE = "https://twitter.com/{}"


async def get_retweets(message: discord.Message, args: tuple):
    match = re.search(r'/status/[0-9]+', args[0])
    if match:
        tweet_id = match.group().split("/")[-1]
    else:
        return await message.reply("Invalid tweet link.")
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(["position", "user_profile_url", "followers", "type"])
    quote_users = []
    for resp in tweepy.Paginator(
            method=client.get_quote_tweets,
            id=tweet_id,
            expansions=["author_id"],
            tweet_fields=["author_id"],
    ):
        quotes = resp.data if resp.data else []
        for tweet in quotes:
            acc = next((a for a in resp.includes["users"] if a.id == tweet.author_id))
            quote_users.append(acc.username)
    r = 0
    for resp in tweepy.Paginator(
            method=client.get_retweeters,
            id=tweet_id,
            user_fields=["public_metrics"],
            max_results=100
    ):
        retweet_by = resp.data if resp.data else []
        for acc in retweet_by:
            r += 1
            atype = "quote" if acc.username in quote_users else "retweet"
            writer.writerow([r, PROFILE_BASE.format(acc.username), acc.public_metrics['followers_count'], atype])
    out.seek(0)
    file = discord.File(fp=out, filename="retweets.csv")
    q = len(quote_users)
    await message.reply(f"{r-q} retweets and {q} quotes:", file=file)