import asyncio
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

load_dotenv()

client = discord.Client(intents=intents)

mongoClient = pymongo.MongoClient(os.getenv("MONGODB_URI"))


db = mongoClient["CinnamonRSS"]

collection = db["user_data"]


@bot.event
async def on_ready():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(feedRunner, "interval", minutes=3)
    scheduler.start()
    print(pyfiglet.figlet_format("Cinnamon RSS", justify="center"))
    print(
        "   ------------------------------------------------------------------------   "
    )


# command used for testing and troubleshooting
@bot.command()
async def tester(ctx, arg):
    feed = feedparser.parse(arg)
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
            embed.set_footer(text=entry.published)
            user = await bot.fetch_user(user_id)
            await user.send(embed=embed)
        # if "category" in entry:
        #     categories = entry.category
        #     user = await bot.fetch_user(user_id)
        #     if "TERM" in categories:
        #         await user.send(f"{categories}")
        #         title = html.fromstring(entry.title).text_content()
        #         link = html.fromstring(entry.link).text_content()
        #         user = await bot.fetch_user(user_id)
        #         await user.send(f"**{title}**\n{link}")
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
        # queries mongodb to check if the user already exists
        user_query = {"user_id": ctx.message.author.id}
        feed = feedparser.parse(args[0])
        link = feed.entries[0].link
        # if the user does not exist, create new document in mongodb
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
        # if the user does exist, find the user and update their rss feed section to include the new feed they've subscribed to
        else:
            user = collection.find(user_query)
            url = args[0]
            for found_user in user:
                # checks if feed url already exists so you can't subscribe twice
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
    # if they are subscribing with keywords and a keyword search parameter, do the same thing
    # as above but taking into account the extra information
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


# "force" a subscription to an RSS feed to bypass any errors
# aka does not run validate function to check if the rss feed is valid before subscribing
# if you know an rss feed is valid but still returns errors use this command
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
        if message == "**Subscribed!**":
            await ctx.send("The link is valid!")
        if error_message != "no_error":
            await ctx.send(error_message)
        if error_message2 != "no_error":
            await ctx.send(error_message2)


# use: unsubscribe <link>
# deletes item from mongodb
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


# used to delete messages when testing/troubleshooting
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)


async def feedChecker(data):
    user_id = data["user_id"]
    feed = feedparser.parse(data["feed_url"])
    x = 0
    if feed.entries[0].link == data["last_link"]:
        x = 0
    else:
        for item in feed.entries:
            if item.link != data["last_link"]:
                x += 1
            else:
                break
    for entry in feed.entries[:x]:
        if data["keyword_search"] == None:
            # creates a discord embedded image if there is media linked
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
                embed.set_footer(text=entry.published)
                channel = await bot.fetch_channel(int(data["channel_id"]))
                await channel.send(embed=embed)
                update = {"$set": {"rss_feeds.$.last_link": feed.entries[0].link}}
                collection.update_one(
                    {
                        "user_id": user_id,
                        "rss_feeds.feed_url": data["feed_url"],
                    },
                    update,
                )
            elif (
                "title" in entry and "link" in entry and "media_thumbnail" not in entry
            ):
                title = html.fromstring(entry.title).text_content()
                link = html.fromstring(entry.link).text_content()
                channel = await bot.fetch_channel(int(data["channel_id"]))
                await channel.send(f"**{title}**\n{link}")
                update = {"$set": {"rss_feeds.$.last_link": feed.entries[0].link}}
                collection.update_one(
                    {
                        "user_id": user_id,
                        "rss_feeds.feed_url": data["feed_url"],
                    },
                    update,
                )
            else:
                link = html.fromstring(entry.link).text_content()
                channel = await bot.fetch_channel(int(data["channel_id"]))
                await channel.send(link)
                update = {"$set": {"rss_feeds.$.last_link": feed.entries[0].link}}
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
                        channel = await bot.fetch_channel(int(data["channel_id"]))
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
            if data["keyword_search"] == "category":
                if "category" in entry:
                    categories = entry.category
                    for keyword in data["keywords"]:
                        if keyword in categories:
                            if "title" in entry:
                                title = html.fromstring(entry.title).text_content()
                                link = html.fromstring(entry.link).text_content()
                                channel = await bot.fetch_channel(
                                    int(data["channel_id"])
                                )
                                await channel.send(f"**{title}**\n{link}")
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
                            else:
                                link = html.fromstring(entry.link).text_content()
                                channel = await bot.fetch_channel(
                                    int(data["channel_id"])
                                )
                                await channel.send(f"{link}")
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

    await asyncio.sleep(1)


# queries mongodb to retrieve rss feed information
# sends discord message if there is a new item in feed
async def feedRunner():
    await bot.wait_until_ready()
    if collection.estimated_document_count() >= 1:
        result = list(collection.find({}).limit(1))
        new_result = loads(dumps(result))
        user_id = int(new_result[0]["user_id"])
        arr = []
        for item in new_result[0]["rss_feeds"]:
            data = {
                "feed_url": item["feed_url"],
                "keyword_search": item["keyword_search"],
                "keywords": item["keywords"],
                "last_link": item["last_link"],
                "channel_id": int(item["channel_id"]),
                "user_id": user_id,
            }
            arr.append(data)
        coroutines = [feedChecker(data) for data in arr]
        await asyncio.gather(*coroutines)


# when the "bookmark" reaction is added to a message:
# the message is copied over to the bookmark channel and the bookmark reaction gets removed after 10 seconds
# when the message is in the bookmark channel, a "saved" reaction is added
# when the saved reaction is clicked on again, this indicates that you want to removethe bookmark so the
# message in the bookmark channel gets deleted
@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == "bookmark_pink":
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        embeds = message.embeds
        embed_title = ""
        desc = ""
        image = ""
        footer_text = ""
        for embed in embeds:
            embed_title = embed.title
            desc = embed.description
            image = embed.image.url
            footer_text = embed.footer.text
        # if message is an embedded message (aka if it contains an image)
        # create a "new" embedded message and send to as a bookmark
        if footer_text != None and image != None:
            embed = discord.Embed(
                title=embed_title, description=desc, color=discord.Color.random()
            )
            embed.set_image(url=image)
            embed.set_footer(text=footer_text)
            bookmark_channel = await bot.fetch_channel(os.getenv("BOOKMARK_CHANNEL"))
            reaction = discord.utils.get(message.reactions, emoji=payload.emoji)
            bookmark_message = await bookmark_channel.send(embed=embed)
            await bookmark_message.add_reaction("<:saved:1120203780823203940>")
            await asyncio.sleep(10)
            await reaction.remove(payload.member)
        else:
            bookmark_channel = await bot.fetch_channel(os.getenv("BOOKMARK_CHANNEL"))
            msg = message.content
            reaction = discord.utils.get(message.reactions, emoji=payload.emoji)

            bookmark_message = await bookmark_channel.send(msg)
            await bookmark_message.add_reaction("<:saved:1120203780823203940>")
            await asyncio.sleep(10)

            await reaction.remove(payload.member)
    if payload.emoji.name == "saved":
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = discord.utils.get(message.reactions, emoji=payload.emoji)
        if reaction.count == 2:
            await message.delete()


asyncio.run(bot.run(os.getenv("DISCORD_TOKEN")))
