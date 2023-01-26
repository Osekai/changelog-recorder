import discord
import json
import datetime
import requests
import time
from dateutil import parser
from discord.ext import tasks
import config

client = discord.Client()

changelog_channel = config.channel


@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))
    await client.change_presence(activity=discord.Game(name="osekai"))
    await get_changelog()
    await client.close()


async def get_changelog():
    channel = client.get_channel(changelog_channel)
    x = json.loads(str(requests.get("https://api.github.com/repos/osekai/osekai/pulls?state=closed&per_page=100").text))
    xf = [];
    for pr in x:
        if pr['merged_at'] is not None:
            xf.append(pr)
    x = sorted(xf, key=lambda y: y['merged_at'])
    messages = [[]];
    index = 0
    counter = 0
    for pr in x:
        if pr['merged_at'] is not None:
            date = parser.parse(pr['merged_at'])
            date = date.replace(tzinfo=None)
            difference = datetime.datetime.utcnow() - date
            if difference.days == 0:
                tags = "";
                labels = sorted(pr['labels'], key=lambda y: y['name'])
                for label in labels:
                    tags += "`" + label['name'] +"`, "
                tags = tags[:len(tags) - 2]
                tempmessage = ["*[" + pr['user']['login'] + "]* " + pr['title'], "[#" + str(pr['number']) + "](" + pr['html_url'] + ") - " + date.strftime('%Y-%m-%d %H:%M') + " UTC\nTags: "+tags+""]
                counter += 1
                if(counter > 24):
                    counter = 0
                    index += 1
                    messages.append([])
                messages[index].append(tempmessage)
    
    #print(message);
    today = datetime.datetime.today() - datetime.timedelta(hours=0, minutes=50)
    for message in messages:
        embed=discord.Embed(title="Osekai Update - " + today.strftime('%Y-%m-%d'), description="The latest updates to osekai today!")
        for field in message:
            embed.add_field(name=field[0], value=field[1], inline=False)
        await channel.send(embed=embed)


    # TODO: send to osekai server apis


client.run(config.token)
