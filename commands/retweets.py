import discord
from catch.catch_tweets import client
import tweepy
import csv
from io import StringIO


async def get_retweets(message: discord.Message, args: tuple):
    link_parts = args[0].split("/")
    tweet_id = link_parts[-1]
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(["username", "followers", "position"])
    i = 0
    for resp in tweepy.Paginator(
            method=client.get_retweeters,
            id=tweet_id,
            user_fields=["public_metrics"],
            max_results=100
    ):
        retweet_by = resp.data if resp.data else []
        for acc in retweet_by:
            i += 1
            writer.writerow([acc.username, acc.public_metrics['followers_count'], i])
    out.seek(0)
    file = discord.File(fp=out, filename="retweets.csv")
    await message.reply(f"**{i}** users retweeted:", file=file)


