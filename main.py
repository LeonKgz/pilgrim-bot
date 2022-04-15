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


async def call_bible_api(lang, book_name, numbers_string, channel):

    version = lang
    passage_name = book_name
    numbers = numbers_string

    russian_books_to_code = {
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
      "Колоссяне": "Col",
      "1Фессалоникийцы": "1Th",
      "2Фессалоникийцы": "2Th",
      "1Тимофей": "1Tim",
      "2Тимофей": "2Tim",
      "Тит": "Titus",
      "Филимон": "Philemon",
      "Евреи": "Hebrews",
      "Откровение": "Rev",
      "Исаия": "Isaiah",
    }

    full_russian_names = {
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
      "Колоссяне": "Послание к Колоссянам",
      "1Фессалоникийцы": "1-е послание к Фессалоникийцам",
      "2Фессалоникийцы": "2-е послание к Фессалоникийцам",
      "1Тимофей": "1-е послание к Тимофею",
      "2Тимофей": "2-е послание к Тимофею",
      "Тит": "Послание к Титу",
      "Филимон": "Послание к Филимону",
      "Евреи": "Послание к Евреям",
      "Откровение": "Откровение Иоанна Богослова",
      "Исаия": "Книга пророка Исаии",
    }

    ukranian_books_to_code = {
      "Матей": "Matthew",
      "Марко": "Mark",
      "Лука": "Luke",
      "Йоан": "John",
      "Діяння": "Acts",
      "Яків": "James",
      "1Петро": "1Peter",
      "2Петро": "2Peter",
      "1Йоан": "1John",
      "2Йоан": "2John",
      "3Йоан": "3John",
      "Юда": "Jude",
      "Римляни": "Rom",
      "1Корінтяни": "1Corinthians",
      "2Корінтяни": "2Corinthians",
      "Галати": "Gal",
      "Ефесяни": "Eph",
      "Филипяни": "Philippians",
      "Колосяни": "Col",
      "1Солуняни": "1Th",
      "2Солуняни": "2Th",
      "1Тимотей": "1Tim",
      "2Тимоьей": "2Tim",
      "Тит": "Titus",
      "Филимон": "Philemon",
      "Євреї": "Hebrews",
      "Одкровення": "Rev ",
    }

    full_ukranian_names = {
      "Матей": "Євангеліє від св. Матвія",
      "Марко": "Євангеліє від св. Марка",
      "Лука": "Євангеліє від св. Луки",
      "Йоан": "Євангеліє від св. Івана",
      "Діяння": "Діяння святих апостолів",
      "Яків": "Соборне послання св. апостола Якова",
      "1Петро": "Перше соборне послання св. апостола Петра",
      "2Петро": "Друге соборне послання св. апостола Петра",
      "1Йоан": "Перше соборне послання св. апостола Івана",
      "2Йоан": "Друге соборне послання св. апостола Івана",
      "3Йоан": "Третє соборне послання св. апостола Івана ",
      "Юда": "Соборне послання св. апостола Юди",
      "Римляни": "Послання св. апостола Павла до римлян",
      "1Корінтяни": "Перше послання апостола Павла до коринфян",
      "2Корінтяни": "Друге послання апостола Павла до коринфян",
      "Галати": "Послання св. апостола Павла до галатів",
      "Ефесяни": "Послання св. апостола Павла до ефесян",
      "Филипяни": "Послання св. апостола Павла до филипян",
      "Колосяни": "Послання св. апостола Павла до колосян",
      "1Солуняни": "Перше послання св. апостола Павла до солунян",
      "2Солуняни": "Друге послання св. апостола Павла до солунян",
      "1Тимотей": "Перше послання св. апостола Павла до Тимофія",
      "2Тимоьей": "Друге послання св. апостола Павла до Тимофія",
      "Тит": "Послання св. апостола Павла до Тит",
      "Филимон": "Послання св. апостола Павла до Филимона",
      "Євреї": "Послання до євреїв",
      "Одкровення": "Обявлення св. Івана Богослова",
    }

    full_names = {
      "рус": full_russian_names,
      "укр": full_ukranian_names,
    }

    books_to_code = {
      "рус": russian_books_to_code,
      "укр": ukranian_books_to_code,
    }
    
    versions = {
      "рус": "synodal",
      "укр": "ukranian",
    }

    try:
      name = full_names[version][passage_name]
      passage = books_to_code[version][passage_name]
      version = versions[version]
    except Exception as e:
      print(e)
      # If version is not specified use one of API's 
      version = version
      passage = passage_name
      name = passage_name

    url = f"https://getbible.net/json?passage={passage}%20{numbers}&version={version}"
    print(url)

    response = requests.get(url)
    try: #try parsing to dict
      dataform = str(response.text).strip("'<>() ").replace('\'', '\"')
    #  print(dataform[:-2])
      dataform = dataform[:-2]
      struct = json.loads(dataform)
      
      if (struct["type"] == "verse"):
        # TODO make a dictionaru mapping json return names to russian or ukrainian full translation.
        # Currently its working for russian only
        #name = struct["book"][0]["book_name"]
        #name = full_russian_names[passage_name]
        
        rets = [f"**{name}**\n"]
        total_size = len(rets[0])

        curr_chapter = "None"

        for b in struct["book"]:
          chapter = b["chapter_nr"]
          if (curr_chapter != chapter):
            rets[-1] += "\n"
          curr_chapter = chapter
          
          for key in list(b["chapter"].keys()):
            verse = key
            content = b["chapter"][key]["verse"]
  #          rets[-1] += f"`  {chapter:>2}:{verse:<2}  `  {content}"
            
            size = len(f"`  {chapter:>2}:{verse:<2}  `  {content}")
            
            if total_size + size >= 2000:
              total_size = 0
              rets.append("") 

            total_size += size
            rets[-1] += f"`  {chapter:>2}:{verse:<2}  `  {content}"

        for r in rets: 
          await channel.send(f"{r}")

        #await ctx.channel.send(f"{ret}")

      elif struct["type"] == "chapter":
        name = struct["book_name"]
        name = full_russian_names[passage_name]

        rets = [f"**{name}**\n\n"]
        total_size = len(rets[0])

        chapter = struct["chapter_nr"]
        for key in list(struct["chapter"].keys()):
          verse = key
          content = struct["chapter"][key]["verse"]

          size = len(f"`  {chapter:>2}:{verse:<2}  `  {content}")

          if total_size + size >= 2000:
            total_size = 0
            rets.append("") 

          total_size += size

          rets[-1] += f"`  {chapter:>2}:{verse:<2}  `  {content}"
        
        for r in rets: 
          await channel.send(f"{r}")

    except Exception as e:
      #print(e)
      print(e)

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
      print("DEBUG: counter is zero (no entries in the verse databse)")
      return

    limit = counter
    
    try:
      sql = f"SELECT * FROM counters WHERE ID = \"verses\""
      cursor.execute(sql)
      counter = int(cursor.fetchone()['Value'])
      current_offset = counter
      counter += 1
      if (counter > limit - 1):
        counter = 0
    except Exception as e:
      print(e)
      db.rollback()
      return
    
    db, cursor = get_db_cursor()
    try:
      sql = f"REPLACE INTO counters(ID, Value) VALUES(\"verses\", {counter})"
      cursor.execute(sql)
      db.commit()

    except Exception as e:
      print(e)
      db.rollback()
      return

    db.close()

    #success = False
    #while not success:
    #  try:
    #    with open('counter.txt', 'r+') as f:
    #      current_offset = int(f.readlines()[0])
    #      
    #      f.seek(0)
    #      if (current_offset >= counter - 1):
    #        f.write("0")
    #      else:
    #        f.write(f"{current_offset + 1}")

    #      f.truncate()

    #      f.close()
    #      break
    #  except Exception as e:
    #    print(f"Write to counter file FAILED: \t\t\t{e}")
    #    continue

    print(f"DEBUG: Current offset: {current_offset}")
    db, cursor = get_db_cursor()
    
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
    print(f"DEBUG: CONTENT IS \t\t\t{content}\n--------------")

    #########################################################


    args = str(content)  
    args = args.split(" ")
    passage_name = args[1]
    version = args[0]
    #numbers = ",%20".join(args[1:])
    numbers = ";".join(args[2:])

    for ch in guild.channels:
      #if ("технический" in ch.name):
      if ("ріка-любові" in ch.name):
        await call_bible_api("рус", passage_name, numbers, ch)

news_alert.start()

@bot.command(name="bible")
async def bible(ctx, *, args=None):
  args = str(args)  
  args = args.split(" ")
  passage_name = args[1]
  version = args[0]
  #numbers = ",%20".join(args[1:])
  numbers = ";".join(args[2:])

  await call_bible_api(version, passage_name, numbers, ctx.channel)


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
