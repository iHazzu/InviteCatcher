import discord
from keys import TWITTER_BEARER_TOKEN
import re
import requests
from wordpress.wp_api import WpApi
import tweepy
from collections import namedtuple


POST_TYPE = "tweet"
URL_REGEX = re.compile(r'(https?://[^\s]+)')
TWEET_PATTERN = re.compile(r'twitter\.com/[\w.-]+/status/[0-9]+')
client = tweepy.Client(TWITTER_BEARER_TOKEN)
Tweet = namedtuple("Tweet", "id text author_id author_name author_image author_bio")


async def go(message: discord.Message, wp: WpApi):
    tweet_links = TWEET_PATTERN.findall(message.content)
    for tweet_link in tweet_links:
        tweet_id = int(tweet_link.split("/")[-1])
        resp = client.get_tweet(id=tweet_id, expansions="author_id", user_fields=["profile_image_url", "description"])
        author = resp.includes["users"][0]
        img_url = author.profile_image_url.replace("_normal", "")
        tweet = Tweet(resp.data.id, resp.data.text, author.id, author.username, img_url, author.description)
        publish_tweet(tweet, wp)


def publish_tweet(tweet: Tweet, wp: WpApi):
    post = wp.get_post(POST_TYPE, f"[{tweet.author_id}]")
    if not post:
        desc = f'<i>{tweet.author_bio}</i>\n' \
               f'<a href="https://twitter.com/{tweet.author_name}" target="_blank">View Profile</a>' \
               f'<!-- Account ID: [{tweet.author_id}] -->' \
               f'<hr/>'
        desc += link_tweet_text(tweet)
        filename = f"{tweet.author_name}.jpg"
        file = requests.get(tweet.author_image).content
        media_id = wp.upload_image(filename, file)["id"]
        wp.create_post(POST_TYPE, tweet.author_name, desc, media_id)
    else:
        if str(tweet.id) not in post['content']['rendered']:
            desc = post['content']['rendered'] + "<hr/>" + link_tweet_text(tweet)
            wp.edit_post(POST_TYPE, post["id"], desc)


def link_tweet_text(tweet):
    text = URL_REGEX.sub(r'<a href="\1">\1</a>', tweet.text)    # making links clickable
    text += f'\n<a href="https://twitter.com/i/web/status/{tweet.id}" target="_blank">View Tweet</a>'
    return text