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

(See the [async def on_raw_reaction_add](https://github.com/shann99/cinnamon_rss/blob/master/cinnamon_rss.py#L474) section in cinnamon_rss.py)

React to a message with a specific emoji and the message gets copied over to my bookmark channel where a new reaction is added to the message. Click on the new reaction to remove the bookmark. The reaction on the original message disappears after 10 seconds. 



 
