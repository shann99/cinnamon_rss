import json
import os
import xml.etree.ElementTree as ET
from pprint import pprint as pp

import discord
import feedparser
import pyfiglet
import pymongo
import requests
from discord.ext import commands
from dotenv import load_dotenv
from lxml import html
from pymongo import MongoClient

from validate import check_link

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

client = discord.Client(intents=intents)

mongoClient = pymongo.MongoClient(MONGO_URI)

db = mongoClient["DB_NAME"]

collection = db["COLLECTION_NAME"]


@bot.event
async def on_ready():
    print(pyfiglet.figlet_format("Cinnamon RSS", justify="center"))
    print(
        "   ------------------------------------------------------------------------   "
    )


# Usage:
# subscribe to RSS Feed: .subscribe https://rssfeed.link
# subscribe with keywords
#   -> <keyword_search> == the section where you want your keyword to be looked for (aka title, summary, etc.)
#   -> keywords should be comma separated such as: apples, bananas, strawberries
#   -> usage: .subscribe https://rssfeed.link <keyword_search> <keyword> <keyword>
#   -> example: .subscribe https://fruits.com/rss title apples, bananas, strawberries
# feed gets validated with W3 validator (see validate.py)
#  --> unicode errors for rss feeds do get ignored


@bot.command(aliases=["Subscribe", "sub"])
async def subscribe(ctx, *args):
    keywords = []
    if len(args) == 0:
        await ctx.send("Hey! You forgot to include a link")
        exit()
    elif len(args) == 2:
        await ctx.send("Please review directions again")
        exit()
    elif len(args) >= 3:
        for i in args[2:]:
            keyword = i.strip(",")
            keywords.append(keyword)
    else:
        pass

    message, error_message, error_message2 = check_link(args[0])
    if message == "**Subscribed!**" and len(args) == 1:
        user_query = {"user_id": ctx.message.author.id}
        if collection.count_documents(user_query) == 0:
            data = {
                "user_id": ctx.message.author.id,
                "rss_feeds": [
                    {"link": args[0], "keyword_search": None, "keywords": None}
                ],
            }
            collection.insert_one(data)
            await ctx.send(message)
        else:
            user = collection.find(user_query)
            for found_user in user:
                update = {
                    "$push": {
                        "rss_feeds": {
                            "link": args[0],
                            "keyword_search": None,
                            "keywords": None,
                        }
                    },
                }
                collection.update_one({"user_id": ctx.message.author.id}, update)
                await ctx.send(message)

    elif message == "**Subscribed!**" and len(args) >= 3:
        user_query = {"user_id": ctx.message.author.id}
        if collection.count_documents(user_query) == 0:
            data = {
                "user_id": ctx.message.author.id,
                "rss_feeds": [
                    {"link": args[0], "keyword_search": args[1], "keywords": keywords}
                ],
            }
            collection.insert_one(data)
            await ctx.send(message)
        else:
            user = collection.find(user_query)
            for found_user in user:
                update = {
                    "$push": {
                        "rss_feeds": {
                            "link": args[0],
                            "keyword_search": args[1],
                            "keywords": keywords,
                        }
                    },
                }
                collection.update_one({"user_id": ctx.message.author.id}, update)
                await ctx.send(message)

    else:
        await ctx.send(message)
        if error_message != "no_error":
            await ctx.send(error_message)
        if error_message2 != "no_error":
            await ctx.send(error_message2)


@bot.command(aliases=["Validate", "verify", "check", "test"])
async def validate(ctx, arg):
    message, error_message, error_message2 = check_link(arg)
    if len(arg) == 0:
        await ctx.send("Hey! You forgot to include a link")
        exit()
    else:
        await ctx.send(message)
        if error_message != "no_error":
            await ctx.send(error_message)
        if error_message2 != "no_error":
            await ctx.send(error_message2)


# remove feed from db -> need to work on
# @bot.command(aliases=["Unsub", "Unsubscribe", "unsub", "remove"])
# async def unsubscribe(ctx, arg):
#     await ctx.send(f"You've been unsubscribed from {arg}")


# just used for testing to clear out messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)


load_dotenv()
bot.run(os.getenv("TOKEN"))
