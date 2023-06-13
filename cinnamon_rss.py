import datetime
import json
import os
import xml.etree.ElementTree as ET
from pprint import pprint as pp

import discord
import feedparser
import pyfiglet
import pymongo
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bson.json_util import dumps, loads
from discord.ext import commands
from dotenv import load_dotenv
from lxml import html
from pymongo import MongoClient

from validate import check_link

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

client = discord.Client(intents=intents)

mongoClient = pymongo.MongoClient(os.getenv("MONGODB_URI"))


db = mongoClient["CinnamonRSS"]

collection = db["user_data"]


@bot.event
async def on_ready():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(feedChecker, "interval", minutes=5)
    scheduler.start()
    print(pyfiglet.figlet_format("Cinnamon RSS", justify="center"))
    print(
        "   ------------------------------------------------------------------------   "
    )


# tester command to test how message look
@bot.command()
async def tester(ctx):
    feed = feedparser.parse(os.getenv("TEST_LINK"))
    x = 5
    user_id = os.getenv("DISCORD_ID")
    for entry in feed.entries[:x]:
        if "media_thumbnail" in entry:
            entry_title = html.fromstring(entry.title).text_content()
            link = html.fromstring(entry.link).text_content()
            media = entry.media_thumbnail[0]["url"]
            embed = discord.Embed(
                title=entry_title, description=link, color=discord.Color.random()
            )
            embed.set_image(url=media)
            embed.set_footer(text=datetime.datetime.now())
            user = await bot.fetch_user(user_id)
            await user.send(embed=embed)
        else:
            title = html.fromstring(entry.title).text_content()
            link = html.fromstring(entry.link).text_content()
            user = await bot.fetch_user(user_id)
            await user.send(f"**{title}**\n{link}")


@bot.command(aliases=["Subscribe", "sub"])
async def subscribe(ctx, *args):
    keywords = []
    if len(args) == 0:
        await ctx.send("Hey! You forgot to include a link.")
        exit()
    elif len(args) == 2:
        await ctx.send("Please review the command usage.")
        exit()
    elif len(args) >= 3:
        for i in args[2:]:
            keyword = i.strip(",")
            keywords.append(keyword)
    else:
        pass

    message, error_message, error_message2 = check_link(args[0])  # type:ignore
    if message == "**Subscribed!**" and len(args) == 1:
        user_query = {"user_id": ctx.message.author.id}
        feed = feedparser.parse(args[0])
        link = feed.entries[0].link
        if collection.count_documents(user_query) == 0:
            data = {
                "user_id": ctx.message.author.id,
                "rss_feeds": [
                    {
                        "feed_url": args[0],
                        "keyword_search": None,
                        "keywords": None,
                        "last_link": link,
                        "channel_id": ctx.channel.id,
                    }
                ],
            }
            collection.insert_one(data)
            await ctx.send(message)

        else:
            user = collection.find(user_query)
            url = args[0]
            for found_user in user:
                url_match = collection.find_one({"rss_feeds.feed_url": url})
                if url_match == None:
                    update = {
                        "$push": {
                            "rss_feeds": {
                                "feed_url": args[0],
                                "keyword_search": None,
                                "keywords": None,
                                "last_link": link,
                                "channel_id": ctx.channel.id,
                            }
                        },
                    }

                    collection.update_one({"user_id": ctx.message.author.id}, update)
                    await ctx.send(message)
                else:
                    await ctx.send("You're already subscribed to this feed.")

    elif message == "**Subscribed!**" and len(args) >= 3:
        user_query = {"user_id": ctx.message.author.id}
        feed = feedparser.parse(args[0])
        link = feed.entries[0].link
        if collection.count_documents(user_query) == 0:
            data = {
                "user_id": ctx.message.author.id,
                "rss_feeds": [
                    {
                        "feed_url": args[0],
                        "keyword_search": args[1],
                        "keywords": keywords,
                        "last_link": link,
                        "channel_id": ctx.channel.id,
                    }
                ],
            }
            collection.insert_one(data)
            await ctx.send(message)
        else:
            user = collection.find(user_query)
            url = args[0]
            for found_user in user:
                url_match = collection.find_one({"rss_feeds.feed_url": url})
                if url_match == None:
                    update = {
                        "$push": {
                            "rss_feeds": {
                                "feed_url": args[0],
                                "keyword_search": args[1],
                                "keywords": keywords,
                                "last_link": link,
                                "channel_id": ctx.channel.id,
                            }
                        },
                    }
                    collection.update_one({"user_id": ctx.message.author.id}, update)

                    await ctx.send(message)
                else:
                    await ctx.send("You're already subscribed to this feed.")
    else:
        await ctx.send(message)
        if error_message != "no_error":
            await ctx.send(error_message)
        if error_message2 != "no_error":
            await ctx.send(error_message2)


# "force" subscription to RSS feed to bypass any errors
@bot.command(aliases=["Force"])
async def force(ctx, *args):
    keywords = []
    if len(args) == 0:
        await ctx.send("Hey! You forgot to include a link.")
        exit()
    elif len(args) == 2:
        await ctx.send("Please review the command usage.")
        exit()
    elif len(args) >= 3:
        for i in args[2:]:
            keyword = i.strip(",")
            keywords.append(keyword)
    else:
        pass
    message = "**Subscribed!**"
    if len(args) == 1:
        user_query = {"user_id": ctx.message.author.id}
        feed = feedparser.parse(args[0])
        link = feed.entries[0].link
        if collection.count_documents(user_query) == 0:
            data = {
                "user_id": ctx.message.author.id,
                "rss_feeds": [
                    {
                        "feed_url": args[0],
                        "keyword_search": None,
                        "keywords": None,
                        "last_link": link,
                        "channel_id": ctx.channel.id,
                    }
                ],
            }
            collection.insert_one(data)
            await ctx.send(message)
        else:
            user = collection.find(user_query)
            url = args[0]
            for found_user in user:
                url_match = collection.find_one({"rss_feeds.feed_url": url})
                if url_match == None:
                    update = {
                        "$push": {
                            "rss_feeds": {
                                "feed_url": args[0],
                                "keyword_search": None,
                                "keywords": None,
                                "last_link": link,
                                "channel_id": ctx.channel.id,
                            }
                        },
                    }

                    collection.update_one({"user_id": ctx.message.author.id}, update)
                    await ctx.send(message)
                else:
                    await ctx.send("You're already subscribed to this feed.")

    elif len(args) >= 3:
        user_query = {"user_id": ctx.message.author.id}
        feed = feedparser.parse(args[0])
        link = feed.entries[0].link
        if collection.count_documents(user_query) == 0:
            data = {
                "user_id": ctx.message.author.id,
                "rss_feeds": [
                    {
                        "feed_url": args[0],
                        "keyword_search": args[1],
                        "keywords": keywords,
                        "last_link": link,
                        "channel_id": ctx.channel.id,
                    }
                ],
            }
            collection.insert_one(data)
            await ctx.send(message)
        else:
            user = collection.find(user_query)
            url = args[0]
            for found_user in user:
                url_match = collection.find_one({"rss_feeds.feed_url": url})
                if url_match == None:
                    update = {
                        "$push": {
                            "rss_feeds": {
                                "feed_url": args[0],
                                "keyword_search": args[1],
                                "keywords": keywords,
                                "last_link": link,
                                "channel_id": ctx.channel.id,
                            }
                        },
                    }
                    collection.update_one({"user_id": ctx.message.author.id}, update)
                    await ctx.send(message)
                else:
                    await ctx.send("You're already subscribed to this feed.")


@bot.command(aliases=["Validate", "verify", "check", "test"])
async def validate(ctx, arg):
    message, error_message, error_message2 = check_link(arg)  # type:ignore
    if len(arg) == 0:
        await ctx.send("Hey! You forgot to include a link")
        exit()
    else:
        await ctx.send(message)
        if error_message != "no_error":
            await ctx.send(error_message)
        if error_message2 != "no_error":
            await ctx.send(error_message2)


# use: unsubscribe <link>
@bot.command(aliases=["Unsub", "Unsubscribe", "unsub", "remove"])
async def unsubscribe(ctx, arg):
    user_query = {"user_id": ctx.message.author.id}
    user = collection.find(user_query)
    for found_user in user:
        collection.update_one(
            {"user_id": ctx.message.author.id},
            {"$pull": {"rss_feeds": {"feed_url": arg}}},
        )
    await ctx.send(f"You've been unsubscribed from {arg}")


# just used for testing to clear out messages
# only works in channels
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, arg):
    await ctx.channel.id.purge(limit=arg + 1)


async def feedChecker():
    await bot.wait_until_ready()
    print(collection.estimated_document_count())
    if collection.estimated_document_count() >= 1:
        result = list(collection.find({}).limit(1))
        new_result = loads(dumps(result))
        user_id = int(new_result[0]["user_id"])
        channel_id = 0
        arr = []
        for item in new_result[0]["rss_feeds"]:
            data = {
                "feed_url": item["feed_url"],
                "keyword_search": item["keyword_search"],
                "keywords": item["keywords"],
                "last_link": item["last_link"],
            }
            channel_id = int(item["channel_id"])
            arr.append(data)
        for data in arr:
            feed = feedparser.parse(data["feed_url"])
            x = 0
            if feed.entries[0].link == data["last_link"]:
                x = 0
            else:
                for item in feed.entries:
                    if item.link == data["last_link"]:
                        break
                    else:
                        x += 1
            for entry in feed.entries[:x]:
                if data["keyword_search"] == None:
                    if "media_thumbnail" in entry:
                        entry_title = html.fromstring(entry.title).text_content()
                        link = html.fromstring(entry.link).text_content()
                        media = entry.media_thumbnail[0]["url"]
                        embed = discord.Embed(
                            title=entry_title,
                            description=link,
                            color=discord.Color.random(),
                        )
                        embed.set_image(url=media)
                        embed.set_footer(text=datetime.datetime.now())
                        channel = await bot.fetch_channel(channel_id)
                        await channel.send(embed=embed)
                        update = {
                            "$set": {"rss_feeds.$.last_link": feed.entries[0].link}
                        }
                        collection.update_one(
                            {
                                "user_id": user_id,
                                "rss_feeds.feed_url": data["feed_url"],
                            },
                            update,
                        )
                    elif (
                        "title" in entry
                        and "link" in entry
                        and "media_thumbnail" not in entry
                    ):
                        title = html.fromstring(entry.title).text_content()
                        link = html.fromstring(entry.link).text_content()
                        channel = await bot.fetch_channel(channel_id)
                        await channel.send(f"**{title}**\n{link}")
                        update = {
                            "$set": {"rss_feeds.$.last_link": feed.entries[0].link}
                        }
                        collection.update_one(
                            {
                                "user_id": user_id,
                                "rss_feeds.feed_url": data["feed_url"],
                            },
                            update,
                        )
                    else:
                        link = html.fromstring(entry.link).text_content()
                        channel = await bot.fetch_channel(channel_id)
                        await channel.send(link)
                        update = {
                            "$set": {"rss_feeds.$.last_link": feed.entries[0].link}
                        }
                        collection.update_one(
                            {
                                "user_id": user_id,
                                "rss_feeds.feed_url": data["feed_url"],
                            },
                            update,
                        )
                else:
                    if data["keyword_search"] == "title":
                        for keyword in data["keywords"]:
                            if keyword in entry.title:
                                title = html.fromstring(entry.title).text_content()
                                link = html.fromstring(entry.link).text_content()
                                channel = await bot.fetch_channel(channel_id)
                                await channel.send(link)
                                update = {
                                    "$set": {
                                        "rss_feeds.$.last_link": feed.entries[0].link
                                    }
                                }
                                collection.update_one(
                                    {
                                        "user_id": user_id,
                                        "rss_feeds.feed_url": data["feed_url"],
                                    },
                                    update,
                                )


load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))
