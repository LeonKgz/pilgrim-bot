#! /usr/bin/python

# vim: set fileencoding=utf-8:

import asyncio
import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
import pymysql.cursors
import json
import sys
import random
import re
import requests
import datetime
from discord.ext.commands import Bot
#from discord.ext import timers
from discord import FFmpegPCMAudio

# retrieving Discord credentials
TOKEN = str(os.getenv('DISCORD_TOKEN'))
GUILD = int(str(os.getenv('DISCORD_GUILD')))

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="bible")
async def bible(ctx, *, args=None):
  args = str(args)  
  args = args.split(" ")
  passage = args[1]
  version = args[0]
  #numbers = ",%20".join(args[1:])
  numbers = ";".join(args[2:])

  url = f"https://getbible.net/json?passage={passage}%20{numbers}&version={version}"

  response = requests.get(url)
  try: #try parsing to dict
    dataform = str(response.text).strip("'<>() ").replace('\'', '\"')
  #  print(dataform[:-2])
    dataform = dataform[:-2]
    struct = json.loads(dataform)
    
    if (struct["type"] == "verse"):
      name = struct["book"][0]["book_name"]

      ret = f"{name}"
      curr_chapter = "None"

      for b in struct["book"]:
        chapter = b["chapter_nr"]
        if (curr_chapter != chapter):
          ret += "\n"
        curr_chapter = chapter
        
        for key in list(b["chapter"].keys()):
          verse = key
          content = b["chapter"][key]["verse"]
          ret += f"\t{chapter}:{verse}\t{content}"

      await ctx.channel.send(f"{ret}")
    elif struct["type"] == "chapter":
      name = struct["book_name"]

      rets = [f"{name}"]
      total_size = len(rets[0])

      chapter = struct["chapter_nr"]
      for key in list(struct["chapter"].keys()):
        verse = key
        content = struct["chapter"][key]["verse"]

        size = len(f"\t{chapter}:{verse}\t{content}")

        if total_size + size >= 2000:
          total_size = 0
          rets.append("") 

        total_size += size

        rets[-1] += f"\t{chapter}:{verse}\t{content}"
      
      for r in rets: 
        print(len(r))
        await ctx.channel.send(f"{r}")

  except Exception as e:
    print(e)


def get_id(ref):

  try:
    ret = int(ref)
    return ret
  except Exception as e:
    if(str(ref)[2] == '!' or str(ref)[2] == '&'): 
      a = int(str(ref)[3:-1])
    else:
      a = int(str(ref)[2:-1])

    return a

#@bot.command(name="clear")
#async def clear(ctx, num):
#  if not await check_rights(ctx, ['Политбюро ЦКТМГ']):
#    return
#  num = int(num) + 1
#  await ctx.channel.purge(limit=num, check=is_me)

def get_guild():
  for guild in bot.guilds:
    print(guild.name)
    if (guild.name == GUILD):
      return guild

async def check_rights(ctx, acceptable_roles):
  super_roles = acceptable_roles

  try:
    res_roles = ctx.author.roles
  except Exception as e:
    res_roles = bot.get_user(ctx.author.id).roles

  for role in list(map(str, res_roles)):
    if (role in super_roles):
      return True
  response = "**" + str(ctx.author.name) + "**, у тебя нет доступа к этой команде " + str(get(bot.emojis, name='peepoClown'))
  await ctx.send(response)
  return False

#guild = bot.get_guild(GUILD)
bot.run(TOKEN)
