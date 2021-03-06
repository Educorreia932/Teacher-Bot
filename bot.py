import asyncio
import json
import math
import random
import time
import discord
import requests

from discord.ext import commands

token_file = "token.txt"

with open(token_file) as f:
    TOKEN = f.read()

bot = commands.Bot(command_prefix='$')

extensions = ['pin_board']

# Here we load our extensions (cogs) listed above in [extensions].

for extension in extensions:
    try:
        bot.load_extension(extension)

    except Exception as e:
        print(f'Failed to load extension {extension}.')

@bot.event
async def on_ready():
    print(f"\nDiscord.py Version: {discord.__version__}")
    print(f"Logged in as: {bot.user.name} - {bot.user.id}")
    
@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Nicest teacher there is ever.",
                          description="You should be studying.", color=0xeee657)

    # Give info about you here
    embed.add_field(name="Author", value="Skelozard/Raymag")

    # Shows the number of servers the bot is member of.
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")

    # Give users a link to invite thsi bot to their server
    embed.add_field(
        name="Invite", value="https://discord.com/oauth2/authorize?client_id=723158683491762276&permissions=0&scope=bot")

    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx, mode, display_time=0, limit=50000, force_update=False):
    print("stats")
    print("Display_Time: {}\n limit: {}".format(display_time, limit))

    await ctx.send("Retrieving stats...")

    start_time = time.time()

    channel = bot.get_channel(715142746356187195)

    msg_title = ""
    current_page = 1
    total_pages = 1
    items_per_page = 50
    array = []

    def render_msg_list(array, msg="", current_page=1, items_per_page=5):
        subarray = array[((current_page * items_per_page) -
                          items_per_page): ((current_page * items_per_page) - 1)]
        counter = 1

        if current_page > 1:
            counter = (current_page * items_per_page) - items_per_page

        for item in subarray:
            msg += str(counter) + ". " + \
                       str(item[0]) + ": " + str(item[1]) + "\n"
            counter += 1

        return msg

    if mode == "messages":
        try:
            async def get_messages_data(channel, limit):
                users = {}
                msg_title = "**Number of messages per author:**\n\n"
                qnt = 0
                async for message in channel.history(limit=limit):
                    qnt += 1
                    if (message.author.mention not in users):
                        users[message.author.mention] = 1

                    else:
                        users[message.author.mention] += 1
                print("{} messages in total".format(qnt))
                # Users
                array = sorted(
                    users.items(), key=lambda kv: kv[1], reverse=True)
                return array

            async def save_messages_data(array):
                try:
                    with open('./data/messages.json', 'w', encoding='utf-8') as messages_data:
                        json.dump({
                            "timestamp": time.time(),
                            "array": array
                        }, messages_data)
                        print("Saving messages data")
                except:
                    print("Error when saving messages data")

            if force_update == False:
                with open('./data/messages.json', 'r', encoding='utf-8') as messages_data:
                    print("Messages file found")
                    messages_data = json.load(messages_data)
                    ts = time.time()
                    time_difference = ts - messages_data["timestamp"]
                    if time_difference <= 86400:
                        print("Messages file is not obsolet")
                        array = messages_data["array"]
                    else:
                        print("Message file is obsolet ")
                        array = await get_messages_data(channel, limit)
                        await save_messages_data(array)
            else:
                print("Forcing update")
                array = await get_messages_data(channel, limit)
                await save_messages_data(array)
        except:
            print("File not found")
            array = await get_messages_data(channel, limit)
            await save_messages_data(array)
        current_page = 1
        total_pages = math.ceil(len(array)/items_per_page)

    elif mode == "emojis":
        try:
            async def get_emojis_data(channel, limit):
                emojis = {i: 0 for i in bot.emojis}

                msg_title = "**Number of times that each emoji was used\n\n**"

                async for message in channel.history(limit=limit):
                    for reaction in message.reactions:
                        for n in range(reaction.count):
                            try:
                                emojis[reaction.emoji] += 1
                            except:
                                continue

                # Emojis
                array = sorted(
                    emojis.items(), key=lambda kv: kv[1], reverse=True)
                return array

            async def save_emojis_data(array):
                try:
                    with open('./data/emojis.json', 'w', encoding="UTF-8") as emojis_data:
                        subarray = []
                        for i in range(len(array)):
                            subarray.append([array[i][0].id, array[i][1]])
                        json.dump({
                            "timestamp": time.time(),
                            "array": subarray
                        }, emojis_data)
                        print("Saving emojis data")
                except:
                    print("Error when saving emojis data")

            if force_update == False:
                with open('./data/emojis.json', 'r', encoding="UTF-8") as emojis_data:
                    print("Emojis file found")
                    emojis_data = json.load(emojis_data)
                    ts = time.time()
                    time_difference = ts - emojis_data["timestamp"]
                    if time_difference <= 86400:
                        print("Emojis file is not obsolet")

                        subarray = []
                        for i in emojis_data["array"]:
                            subarray.append((bot.get_emoji(i[0]), i[1]))

                        array = subarray
                    else:
                        print("Emoji file is obsolet ")
                        array = await get_emojis_data(channel, limit)
                        await save_emojis_data(array)
            else:
                print("Forcing update")
                array = await get_emojis_data(channel, limit)
                await save_emojis_data(array)

        except:
            print("File not found")
            array = await get_emojis_data(channel, limit)
            await save_emojis_data(array)
        current_page = 1
        total_pages = math.ceil(len(array)/items_per_page)

    else:
        print("Usage: stats emojis/messages <-time>")

    total_time = time.time() - start_time

    async def show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, user, render_msg_list):
        msg = render_msg_list(array, msg_title, current_page, items_per_page)

        embed = discord.Embed(
            title="",
            description=msg[0:1990],
            color=0xeee657
        )
        embed.add_field(
            name='Page', value='{}/{}'.format(current_page, total_pages))
        stats = await ctx.send(embed=embed)

        react_emojis = ['◀️', '▶️']
        for emoji in react_emojis:
            await stats.add_reaction(emoji)

        def check_react(reaction, user):
            if reaction.message.id != stats.id:
                return False
            if str(reaction.emoji) not in react_emojis:
                return False
            if user != ctx.message.author:
                return False
            return True

        try:
            res, user = await bot.wait_for('reaction_add', check=check_react, timeout=30)
            if user != ctx.message.author:
                pass
            elif '◀️' in str(res.emoji) and current_page > 1:
                print('Previous page')
                current_page -= 1
                await show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, user, render_msg_list)
            elif '▶️' in str(res.emoji) and current_page < total_pages:
                print('Next page')
                current_page += 1
                await show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, user, render_msg_list)
        except asyncio.TimeoutError:
            print("Timeout")
            await stats.delete()


    await show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, ctx.message.author, render_msg_list)

    if (display_time == "-time"):
        await ctx.send("Stats completed in " + str(total_time) + " seconds")

@bot.command()
async def what(ctx, word):
    query = requests.get(
        'http://api.urbandictionary.com/v0/define?term=' + word)
    query = query.json()

    try:
        if len(query["list"]) > 0:
            embed = discord.Embed(
                title= "**{}**".format(word.title()),
                description = query["list"][0]["definition"].replace("[", "__").replace("]","__"),
                color= 0xeee657
            )

            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title= "Sorry, I don't know the meaning of this term.",
                color= 0xeee657
            )
            await ctx.send(embed= embed)
    except:
        embed = discord.Embed(
            title = "I'm not feeling well today, please call the dev :(",
            color = 0xeee657
        )
        await ctx.send(embed= embed)

@bot.command()
async def iq(ctx):
    embed = discord.Embed(
        title= "You have a total IQ of " + str(random.randint(1, 201)),
        color= 0xeee657
    )

    await ctx.send(embed= embed)

@bot.command()
async def joke(ctx):
    try:
        query = requests.get(
            "https://sv443.net/jokeapi/v2/joke/Miscellaneous?blacklistFlags=nsfw,religious,political,racist,sexist&type=single")
        query = query.json()

        embed = discord.Embed(
            title= "Here's the joke",
            description= query["joke"],
            color= 0xeee657
        )
        await ctx.send(embed= embed)

    except:
        embed = discord.Embed(
            title = "I'm not feeling well today, please call the dev :(",
            color = 0xeee657
        )

        await ctx.send(embed= embed)

@bot.command()
async def excuse(ctx):
    try:
        excuses = []
        with open('./data/excuses.json', 'r', encoding='utf-8') as excuses:
            excuses = json.load(excuses)

        embed = discord.Embed(
            title= "I'm not with the homework...",
            description= random.choice(excuses),
            color= 0xeee657
        )
        await ctx.send(embed= embed)

    except:
        embed = discord.Embed(
            title= "I'm not feeling well today, please call the dev :(",
            color= 0xeee657
        )

    await ctx.send(embed= embed)

bot.run(TOKEN)
