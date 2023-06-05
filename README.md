# cinnamon_rss
A discord bot to subscribe to RSS feeds

#### ⚠️ Work in Progress !! ⚠️

## COMMANDS

### .subscribe command

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
### .validate command
  
Command to solely validate rss feed links using https://validator.w3.org/ API
  
Usage:
 - .validate https://rssfeed.com/rss


 
