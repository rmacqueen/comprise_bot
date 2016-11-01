import praw
import re
import os
import time
import config_bot

comprise_matcher = re.compile(r'(\bbe\b|\bis\b|\bare\b)\s*comprised\s*\bof\b', re.IGNORECASE)

response = "Hi, I'm a friendly grammar bot. It appears you have used some variation of the " \
"phrase 'comprised of'. Although writers will occasionally use it, 'comprised of' should be avoided, "\
"since the construction introduces unnecessary inconsistency and imprecision " \
"into the English language. 'To comprise' means to include or to be composed of several things. It is therefore illogical "\
"that its grammatical opposite, 'to be comprised of', could mean the same thing. For a more complete argument against its usage, "\
"please see [this wikipedia page](https://en.wikipedia.org/wiki/User:Giraffedata/comprised_of).\n\n"\
"___\n"\
"^I ^am ^a ^bot, ^and ^this ^action ^was ^performed ^automatically. ^If ^you ^have ^feedback ^please ^message ^/u/the_undergroundman"


# Have we run this code before? If not, create an empty list
if not os.path.isfile("comments_replied_to.txt"):
    comments_replied_to = []

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and remove any empty values
    with open("comments_replied_to.txt", "r") as f:
        comments_replied_to = filter(None, f.read().split('\n'))

def handle_ratelimit(func, *args, **kwargs):
    while True:
        try:
            func(*args, **kwargs)
            break
        except praw.errors.RateLimitExceeded as error:
            print '\tSleeping for %d seconds' % error.sleep_time
            time.sleep(error.sleep_time)

def login():
    r = praw.Reddit(config_bot.APP_UA)
    r.set_oauth_app_info(config_bot.APP_ID, config_bot.APP_SECRET, config_bot.APP_URI)
    r.refresh_access_information(config_bot.APP_REFRESH_TOKEN)
    return r

r = login()

subreddit_comments = praw.helpers.comment_stream(r, 'all', limit=None)
for comment in subreddit_comments:
    if comment.body and comment.author.name != config_bot.REDDIT_USERNAME and comment.id not in comments_replied_to and comprise_matcher.search(comment.body):
        print "Replying to " + str(comment.id)
        handle_ratelimit(comment.reply, response)
        comments_replied_to.append(comment.id)
        # Write our updated list back to the file
        with open("comments_replied_to.txt", "a") as f:
            f.write(comment.id + '\n')
