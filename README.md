# cinnamon_rss
A discord bot to subscribe to RSS feeds

#### ⚠️ Work in Progress !! ⚠️

## Cinnamon RSS 

Cinnamon RSS is a discord bot that allows you to use commands to subscribe and manage your subscriptions to RSS feeds and notify you of any updates to your subscription. 

It's coded in Python using the [discord.py](https://pypi.org/project/discord.py/) and [feedparser](https://pypi.org/project/feedparser/) libraries. 

I'm using [MongoDB](https://www.mongodb.com/) for the database to store the RSS feed subscriptions and deployed the app on [Fly.io](https://fly.io/) so that the bot is up 24/7.

---
## Commands

#### .subscribe command

Basic Usage (subscribe to RSS Feed): 
`.subscribe https://rssfeed.com/rss`

Advanced (subscribe with keywords):
   - <keyword_search> = the section where you want your keyword to be looked for (aka title, summary, etc.)
   - keywords should be comma separated such as: apples, bananas, strawberries
   - usage: `.subscribe https://rssfeed.com/rss <keyword_search> <keyword> <keyword>`
   - example: `.subscribe https://fruits.com/rss title apples, bananas, strawberries`


Feed will be validated with W3 validator (see [validate.py](https://github.com/shann99/cinnamon_rss/blob/master/validate.py)) automatically when calling the .subscribe command 
  (unicode errors for RSS feeds get ignored)

---
#### .validate command
  
Command to solely validate RSS feed links using https://validator.w3.org/ API
  
Usage:
 - `.validate https://rssfeed.com/rss`

---
#### .force command
  
Command to "force" a subscription to an RSS feed. Created because the .subscribe command will return any errors after checking the feed is valid using the w3 validator API. This way, you can subscribe to feeds anyway but obviously use at your own discretion.
   
Usage:
 - `.force https://rssfeed.com/rss`

---
#### .tester command

Retrieves the first 5 items in an RSS feed to test how the message will look like. Command is just for testing purposes.
   
Usage:
 - `.tester https://rssfeed.com/rss`

---
#### .clear command
  
Used to delete messages in channels.
   
Usage:
 - `.clear <amount_of_messages>`
  - example: `.clear 6` 

---
### Bookmarks

React to a message with a specific emoji and the message gets copied over to my bookmark channel where a new reaction is added to the message. The reaction to the original message will disappear after 10 seconds.

(See the [async def on_raw_reaction_add](https://github.com/shann99/cinnamon_rss/blob/master/cinnamon_rss.py#L474) section in cinnamon_rss.py)

If you'd like to use this as well, create your own bookmark channel and either create your own environment variable (can be under the name of BOOKMARK_CHANNEL or anything else) or directly copy the bookmark channel's ID to add to your code.

[Where I mention](https://github.com/shann99/cinnamon_rss/blob/master/cinnamon_rss.py#L476) `if payload.emoji.name == "bookmark_pink"`, bookmark_pink is the name of the emoji I created in my server to mean that I want to bookmark something. Simply change bookmark_pink to your own emoji name. 

[Where it says](https://github.com/shann99/cinnamon_rss/blob/master/cinnamon_rss.py#L484): `await bookmark_message.add_reaction("<:saved:1120203780823203940>")` <:saved:1120203780823203940> is the name and id of the emoji.
To retrieve this information about your own emoji, in your server type `\:nameofemoji:` to receive the name:id information.
Example `\:bookmark_pink:` or `\:saved:`

[I also write](https://github.com/shann99/cinnamon_rss/blob/master/cinnamon_rss.py#L489) `if payload.emoji.name == "saved"`. This is the new emoji that I have added to the copied message in the bookmarks channel to show that the message is saved. If you want to change it your own emoji, just change the name. A cavaet here though is that since the bot has already added a reaction of this emoji, when you click on the emoji to "remove" the save, the number of reactions will go up to 2 which is expected. The message will be deleted once the number of reactions on the saved emoji is greater than or equal to 2.


---
## Extra Information

This project is primarily a personal project. Meaning I haven't really put thought into if other people would also use this 🫨🫨. For example, the "bookmark" functionality I added contains the reactions I created in my own server so those are things that would need to be changed if you want to fork this repo.

When using the subscribe command to an RSS feed, whichever Discord channel you subscribe to the RSS feed in will be the Discord channel where you receive updates for that particular feed.
I did it this way because I wanted to separate out the different RSS feeds I'm subscribed to into different channels for organizational purposes.

The keyword functionality (in terms of when checking the feed for updates) is still a work in progress. As of now, it's mostly based on my own use cases so it might change a lot of be completely revamped at some point.


 
