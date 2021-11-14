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

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

def get_db_cursor():
  db = pymysql.connect(host=HOST,
                       user=USER,
                       password=PASSWORD,
                       db=DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
  return db, db.cursor()

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')

@tasks.loop(seconds=3600.0)
async def news_alert():
  guild = bot.get_guild(GUILD) 
  db, cursor = get_db_cursor()

  hour = int(datetime.datetime.now().hour)
  print(f"DEBUG: Current hour is {hour}")

  if (guild and hour == 9):

    counter = None

    try:
      sql = f"SELECT COUNT(*) FROM verses"
      cursor.execute(sql)
      counter = int(cursor.fetchone()['COUNT(*)'])
    except Exception as e:
      print(e)
      db.rollback()
      return

    if (counter == 0):
      return

    with open('counter.txt', 'r+') as f:
      current_offset = int(f.readlines()[0])
      
      f.seek(0)
      if (current_offset >= counter - 1):
        f.write("0")
      else:
        f.write(f"{current_offset + 1}")

      f.truncate()

      f.close()
    
    try:
      sql = f"SELECT * FROM verses ORDER By ID LIMIT 1 OFFSET {current_offset}"
      cursor.execute(sql)
      content = cursor.fetchone()['Info_Rus']
    except Exception as e:
      print(e)
      try:
        db.rollback()
      except Exception as e:
        print(re)
      return

    db.close()

    #########################################################
    
    args = str(content)  
    args = args.split(" ")
    passage_name = args[1]
    version = args[0]
    #numbers = ",%20".join(args[1:])
    numbers = ";".join(args[2:])

    books = {
      "Матфей": "Matthew",
      "Марк": "Mark",
      "Лука": "Luke",
      "Иоанн": "John",
      "Деяния": "Acts",
      "Иаков": "James",
      "1Петр": "1Peter",
      "2Петр": "2Peter",
      "1Иоанн": "1John",
      "2Иоанн": "2John",
      "3Иоанн": "3John",
      "Иуда": "Jude",
      "Римляне": "Rom",
      "1Коринфяне": "1Corinthians",
      "2Коринфяне": "2Corinthians",
      "Галаты": "Gal",
      "Ефесяне": "Eph",
      "Филиппийцы": "Philippians",
      "Колоссянам": "Col",
      "1Фессалоникийцы": "1Th",
      "2Фессалоникийцы": "2Th",
      "1Тимофей": "1Tim",
      "2Тимофей": "2Tim",
      "Тит": "Titus",
      "Филимон": "Philemon",
      "Евреи": "Hebrews",
      "Откровение": "Rev ",
    }

    book_full_name = {
      "Матфей": "Евангелие от Матфея",
      "Марк": "Евангелие от Марка",
      "Лука": "Евангелие от Луки",
      "Иоанн": "Евангелие от Иоанна",
      "Деяния": "Деяния святых апостолов",
      "Иаков": "Послание Иакова",
      "1Петр": "1-е послание Петра",
      "2Петр": "2-е послание Петра",
      "1Иоанн": "1-е послание Иоанна",
      "2Иоанн": "2-е послание Иоанна",
      "3Иоанн": "3-е послание Иоанна",
      "Иуда": "Послание Иуды",
      "Римляне": "Послание к Римлянам",
      "1Коринфяне": "1-е послание к Коринфянам",
      "2Коринфяне": "2-е послание к Коринфянам",
      "Галаты": "Послание к Галатам",
      "Ефесяне": "Послание к Ефесянам",
      "Филиппийцы": "Послание к Филиппийцам",
      "Колоссянe": "Послание к Колоссянам",
      "1Фессалоникийцы": "1-е послание к Фессалоникийцам",
      "2Фессалоникийцы": "2-е послание к Фессалоникийцам",
      "1Тимофей": "1-е послание к Тимофею",
      "2Тимофей": "2-е послание к Тимофею",
      "Тит": "Послание к Титу",
      "Филимон": "Послание к Филимону",
      "Евреи": "Послание к Евреям",
      "Откровение": "Откровение Иоанна Богослова",
    }
    
    versions = {
      "рус": "synodal",
      "укр": "ukranian",
    }

    passage = books[passage_name]
    version = versions[version]

    url = f"https://getbible.net/json?passage={passage}%20{numbers}&version={version}"

    response = requests.get(url)
    try: #try parsing to dict
      dataform = str(response.text).strip("'<>() ").replace('\'', '\"')
    #  print(dataform[:-2])
      dataform = dataform[:-2]
      struct = json.loads(dataform)
      
      if (struct["type"] == "verse"):
        # TODO make a dictionaru mapping json return names to russian or ukrainian full translation.
        # Currently its working for russian only
        name = struct["book"][0]["book_name"]

        name = book_full_name[passage_name]
        
        ret = f"**{name}**"
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

        for ch in guild.channels:
          if ("ріка-любові" in ch.name):
            await ch.send(f"{ret}")

    except Eception as e:
      print(e)

news_alert.start()

@bot.command(name="bible")
async def bible(ctx, *, args=None):
  args = str(args)  
  args = args.split(" ")
  passage_name = args[1]
  version = args[0]
  #numbers = ",%20".join(args[1:])
  numbers = ";".join(args[2:])

  books = {
    "Матфей": "Matthew",
    "Марк": "Mark",
    "Лука": "Luke",
    "Иоанн": "John",
    "Деяния": "Acts",
    "Иаков": "James",
    "1Петр": "1Peter",
    "2Петр": "2Peter",
    "1Иоанн": "1John",
    "2Иоанн": "2John",
    "3Иоанн": "3John",
    "Иуда": "Jude",
    "Римляне": "Rom",
    "1Коринфяне": "1Corinthians",
    "2Коринфяне": "2Corinthians",
    "Галаты": "Gal",
    "Ефесяне": "Eph",
    "Филиппийцы": "Philippians",
    "Колоссянам": "Col",
    "1Фессалоникийцы": "1Th",
    "2Фессалоникийцы": "2Th",
    "1Тимофей": "1Tim",
    "2Тимофей": "2Tim",
    "Тит": "Titus",
    "Филимон": "Philemon",
    "Евреи": "Hebrews",
    "Откровение": "Rev ",
  }

  book_full_name = {
    "Матфей": "Евангелие от Матфея",
    "Марк": "Евангелие от Марка",
    "Лука": "Евангелие от Луки",
    "Иоанн": "Евангелие от Иоанна",
    "Деяния": "Деяния святых апостолов",
    "Иаков": "Послание Иакова",
    "1Петр": "1-е послание Петра",
    "2Петр": "2-е послание Петра",
    "1Иоанн": "1-е послание Иоанна",
    "2Иоанн": "2-е послание Иоанна",
    "3Иоанн": "3-е послание Иоанна",
    "Иуда": "Послание Иуды",
    "Римляне": "Послание к Римлянам",
    "1Коринфяне": "1-е послание к Коринфянам",
    "2Коринфяне": "2-е послание к Коринфянам",
    "Галаты": "Послание к Галатам",
    "Ефесяне": "Послание к Ефесянам",
    "Филиппийцы": "Послание к Филиппийцам",
    "Колоссянe": "Послание к Колоссянам",
    "1Фессалоникийцы": "1-е послание к Фессалоникийцам",
    "2Фессалоникийцы": "2-е послание к Фессалоникийцам",
    "1Тимофей": "1-е послание к Тимофею",
    "2Тимофей": "2-е послание к Тимофею",
    "Тит": "Послание к Титу",
    "Филимон": "Послание к Филимону",
    "Евреи": "Послание к Евреям",
    "Откровение": "Откровение Иоанна Богослова",
  }
  
  versions = {
    "рус": "synodal",
    "укр": "ukranian",
  }

  passage = books[passage_name]
  version = versions[version]

  url = f"https://getbible.net/json?passage={passage}%20{numbers}&version={version}"

  response = requests.get(url)
  try: #try parsing to dict
    dataform = str(response.text).strip("'<>() ").replace('\'', '\"')
  #  print(dataform[:-2])
    dataform = dataform[:-2]
    struct = json.loads(dataform)
    
    if (struct["type"] == "verse"):
      # TODO make a dictionaru mapping json return names to russian or ukrainian full translation.
      # Currently its working for russian only
      name = struct["book"][0]["book_name"]

      name = book_full_name[passage_name]
      
      ret = f"**{name}**"
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
      name = book_full_name[passage_name]

      rets = [f"**{name}**\n\n"]
      total_size = len(rets[0])

      chapter = struct["chapter_nr"]
      for key in list(struct["chapter"].keys()):
        verse = key
        content = struct["chapter"][key]["verse"]

        size = len(f"{chapter}:{verse}\t{content}")

        if total_size + size >= 2000:
          total_size = 0
          rets.append("") 

        total_size += size

        rets[-1] += f"{chapter}:{verse}\t{content}"
      
      for r in rets: 
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

def is_me(m):
  return True

@bot.command(name="clear")
async def clear(ctx, num):
  #if not await check_rights(ctx, ['Политбюро ЦКТМГ']):
  #  return
  num = int(num) + 1
  await ctx.channel.purge(limit=num, check=is_me)

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
