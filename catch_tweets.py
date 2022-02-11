import discord
from keys import WP_AUTH_HEADER, TWITTER_BEARER_TOKEN
import requests
import re
import tweepy
from collections import namedtuple


WORDPRESS_API_URL = "https://alphaleaks.com/wp-json/wp/v2/"
POST_TYPE = "tweets"
POSTS_URL = WORDPRESS_API_URL + POST_TYPE
URL_REGEX = re.compile(r'(https?://[^\s]+)')
TWEET_PATTERN = re.compile(r'twitter\.com/[\w.-]+/status/[0-9]+')
client = tweepy.Client(TWITTER_BEARER_TOKEN)
Tweet = namedtuple("Tweet", "id text author_id author_name author_image author_bio")


async def go(message: discord.Message):
    tweet_links = TWEET_PATTERN.findall(message.content)
    for tweet_link in tweet_links:
        tweet_id = int(tweet_link.split("/")[-1])
        resp = client.get_tweet(id=tweet_id, expansions="author_id", user_fields=["profile_image_url", "description"])
        author = resp.includes["users"][0]
        img_url = author.profile_image_url.replace("_normal", "")
        tweet = Tweet(resp.data.id, resp.data.text, author.id, author.username, img_url, author.description)
        publish_tweet(tweet)


def publish_tweet(tweet):
    post = get_post(tweet.author_id)
    if not post:
        create_post(tweet)
    else:
        if str(tweet.id) not in post['content']['rendered']:
            edit_post(post, tweet)


def get_post(account_id):
    payload = {
        'post_type': POST_TYPE,
        'search': f"[{account_id}]"
    }
    resp = requests.get(url=POSTS_URL, params=payload, headers=WP_AUTH_HEADER)
    posts = resp.json()
    if posts:
        return posts[0]
    else:
        return None


def create_post(tweet):
    image = upload_image(tweet)
    desc = f'<i>{tweet.author_bio}</i>\n' \
           f'<a href="https://twitter.com/{tweet.author_name}" target="_blank">View Profile</a>' \
           f'<!-- Account ID: [{tweet.author_id}] -->' \
           f'<hr/>'
    desc += link_tweet_text(tweet)
    payload = {
        'title': tweet.author_name,
        'content': desc,
        'status': 'publish',
        'featured_media': image["id"]
    }
    requests.post(url=POSTS_URL, data=payload, headers=WP_AUTH_HEADER)


def upload_image(tweet):
    img_data = requests.get(tweet.author_image).content
    headers = WP_AUTH_HEADER.copy()
    headers['Content-Type'] = f'image/jpg'
    headers['Content-Disposition'] = f'attachment; filename="{tweet.author_name}.jpg"'
    url = WORDPRESS_API_URL + "media"
    resp = requests.post(url=url, data=img_data, headers=headers)
    return resp.json()


def edit_post(post_data, tweet):
    desc = post_data['content']['rendered'] + "<hr/>" + link_tweet_text(tweet)
    payload = {
        'id': post_data['id'],
        'content': desc
    }
    url = POSTS_URL + f"/{post_data['id']}"
    requests.post(url=url, data=payload, headers=WP_AUTH_HEADER)


def link_tweet_text(tweet):
    text = URL_REGEX.sub(r'<a href="\1">\1</a>', tweet.text)    # making links clickable
    text += f'\n<a href="https://twitter.com/i/web/status/{tweet.id}" target="_blank">View Tweet</a>'
    return text