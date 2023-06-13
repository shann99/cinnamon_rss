# cinnamon_rss
A discord bot to subscribe to RSS feeds

#### ⚠️ Work in Progress !! ⚠️

## Cinnamon RSS 

Cinnamon RSS is a discord bot that allows you to use commands to subscribe and manage your subscriptions to RSS feeds and notify you of any updates to your subscription. 

It's coded in Python using primarily the [discord.py](https://pypi.org/project/discord.py/) and [feedparser](https://pypi.org/project/feedparser/) libraries. 

It uses MongoDB as it's database to store the rss feed subscriptions and it's deployed on Fly.io so that the bot is up 24/7. 



---

## COMMANDS

#### .subscribe command

Basic Usage (subscribe to RSS Feed): 
- .subscribe https://rssfeed.com/rss

Advanced (subscribe with keywords):
   - <keyword_search> = the section where you want your keyword to be looked for (aka title, summary, etc.)
   - keywords should be comma separated such as: apples, bananas, strawberries
   - usage: .subscribe https://rssfeed.com/rss <keyword_search> <keyword> <keyword>
   - example: .subscribe https://fruits.com/rss title apples, bananas, strawberries


Feed will be validated with W3 validator (see validate.py) automatically when calling the .subscribe command 
  (unicode errors for rss feeds do get ignored)

---
#### .validate command
  
Command to solely validate rss feed links using https://validator.w3.org/ API
  
Usage:
 - .validate https://rssfeed.com/rss

---
#### .force command
  
Command to "force" a subscription to an rss feed. Created because the .subscribe command will return any errors after checking the feed is valid using the w3 validator API. This way, you can subscribe to feeds anyway but obviously use at your own discretion.
   
Usage:
 - .force https://rssfeed.com/rss

---
#### .tester command

Retrieves the first 5 items in an RSS feed to test how the message will look like. Literally just for testing purposes.
   
Usage:
 - .tester https://rssfeed.com/rss

---
#### .clear command
  
Used to delete messages in channels. It will clear the number of messages you want to delete
   
Usage:
 - .clear <amount_of_messages>
  - example: .clear 6 



 
 
