import json
import os
import xml.etree.ElementTree as ET
from pprint import pprint as pp

import discord
import feedparser
import pyfiglet
import requests
from discord.ext import commands
from dotenv import load_dotenv
from lxml import html

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

client = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(pyfiglet.figlet_format("Cinnamon RSS", justify="center"))
    print(
        "   ------------------------------------------------------------------------   "
    )


# usage: .subscribe https://rssfeed.link
# will first check the link against w3 rss feed validator API to ensure its valid before subscribing
@bot.command(aliases=["Subscribe", "sub"])
async def subscribe(ctx, arg):
    base_url = "http://validator.w3.org/feed/check.cgi?url="
    validator = requests.post(base_url + arg + "&output=soap12")
    status = validator.status_code
    resp_length = len(validator.content)

    response = validator.text

    # success
    if status == 200:
        root = ET.fromstring(response)
        ns = {"env": "Envelope", "m": "http://www.w3.org/2005/10/feed-validator"}
        error_nums = root.find(".//m:errorcount", ns)

        if int(error_nums.text) > 0:  # type: ignore
            await ctx.send(
                "There seems to be an error regarding your RSS feed link.\nBelow are the error(s): "
            )

            a = root.iterfind(".//m:errorlist/error/type", ns)
            b = root.iterfind(".//m:errorlist/error/text", ns)
            for error_type, error_text in zip(a, b):
                await ctx.send(f"**{error_type.text}** -> {error_text.text}")

        else:
            await ctx.send("**Subscribed!**")
            feed = feedparser.parse(arg)
            for entry in feed.entries:
                if "title" in entry and "summary" in entry and "link" in entry:
                    title = html.fromstring(entry.title).text_content()
                    link = html.fromstring(entry.link).text_content()
                    await ctx.send(f"**{title}**\n{link}")

    # error status
    elif status == 301:
        if resp_length > 2000:
            await ctx.send(f"**{status} Moved Permanently**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Moved Permanently**")
            await ctx.send("**Error Message**: \n> {}".format(validator.content))
    elif status == 308:
        if resp_length > 2000:
            await ctx.send(f"**{status} Permanent Redirect**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Permanent Redirect**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))
    elif status == 401:
        if resp_length > 2000:
            await ctx.send(f"**{status} Unauthorized**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Unauthorized**")
            await ctx.send("**Error Message**: \n> {}".format(validator.content))
    elif status == 403:
        if resp_length > 2000:
            await ctx.send(f"**{status} Forbidden Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Forbidden**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    elif status == 404:
        if resp_length > 2000:
            await ctx.send(f"**{status} Not Found Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Not Found Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))
    elif status == 500:
        if resp_length > 2000:
            await ctx.send(f"**{status} Internal Server Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Internal Server Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    elif status == 502:
        if resp_length > 2000:
            await ctx.send(f"**{status} Bad Gateway Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Bad Gateway Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    elif status == 504:
        if resp_length > 2000:
            await ctx.send(f"**{status} Gateway Timeout Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Gateway Timeout Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    else:
        if resp_length > 2000:
            await ctx.send(f"**{status} code**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} code**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    await ctx.send(arg)


@bot.command(aliases=["Validate", "verify", "check", "test"])
async def validate(ctx, arg):
    base_url = "http://validator.w3.org/feed/check.cgi?url="
    validator = requests.post(base_url + arg + "&output=soap12")
    resp_length = len(validator.content)
    status = validator.status_code

    if status == 200:
        await ctx.send("**This is a valid RSS feed!**")
    elif status == 301:
        if resp_length > 2000:
            await ctx.send(f"**{status} Moved Permanently**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Moved Permanently**")
            await ctx.send("**Error Message**: \n> {}".format(validator.content))
    elif status == 308:
        if resp_length > 2000:
            await ctx.send(f"**{status} Permanent Redirect**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Permanent Redirect**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))
    elif status == 401:
        if resp_length > 2000:
            await ctx.send(f"**{status} Unauthorized**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Unauthorized**")
            await ctx.send("**Error Message**: \n> {}".format(validator.content))
    elif status == 403:
        if resp_length > 2000:
            await ctx.send(f"**{status} Forbidden Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Forbidden**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    elif status == 404:
        if resp_length > 2000:
            await ctx.send(f"**{status} Not Found Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Not Found Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))
    elif status == 500:
        if resp_length > 2000:
            await ctx.send(f"**{status} Internal Server Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Internal Server Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    elif status == 502:
        if resp_length > 2000:
            await ctx.send(f"**{status} Bad Gateway Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Bad Gateway Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    elif status == 504:
        if resp_length > 2000:
            await ctx.send(f"**{status} Gateway Timeout Error**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} Gateway Timeout Error**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))

    else:
        if resp_length > 2000:
            await ctx.send(f"**{status} code**")
            await ctx.send("**Error Message**:\n> {}".format(validator.content[:1900]))
            await ctx.send("**Continued**:\n> {}".format(validator.content[1901:]))

        else:
            await ctx.send(f"**{status} code**")
            await ctx.send("**Error Message:** \n> {}".format(validator.content))


@bot.command(aliases=["Unsub", "Unsubscribe", "unsub", "remove"])
async def unsubscribe(ctx, arg):
    await ctx.send(f"You've been unsubscribed from {arg}")


load_dotenv()
bot.run(os.getenv("TOKEN"))
# **Cinnamon RSS Actions**:
# - Type '$help' for help
# - Type '$validate <link>' for cinnamon rss to check if the RSS link you've provided is valid (this is done using an API request to https://validator.w3.org/)
# - Type '$subscribe <link>' in which cinnamon rss will first automatically check the RSS feed link to see if it's valid and if it is, it will subscribe and alert you to any new updates
# - ? Type '$subscribe <link> <keywords:keyword>' to subscribe to an RSS feed and only get updated if the feed is updated with your keywords. The keywords need to be comma separated.
#     Ex. $subscribe https://rssfeed.link keywords:food, drink, movie
#     or $subscribe https://rssfeed.link keywords:food
