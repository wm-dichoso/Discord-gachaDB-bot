import os
import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
test_CHANNEL_ID = os.getenv('test_CHANNEL_ID')


@dataclass
class Quest_Session:
    is_active: bool = False
    start_time: int = 0
    break_start : int = 0
    break_duration: int = 0
    has_breakTime: bool = False
    quest_name: str = "Quest"

    def reset(self):
        Quest_Session.is_active = False
        Quest_Session.start_time: int = 0
        Quest_Session.break_start = 0
        Quest_Session.break_duration = 0
        Quest_Session.has_breakTime = False
        Quest_Session.quest_name = "Quest"

    def Session_Activate(self):
        Quest_Session.is_active = True

    def Set_QuestName(self, name):
        Quest_Session.quest_name = name

    @property
    def is_on_break(self):
        return self.break_start != 0

    @property
    def had_breaks(self):
        return self.has_breakTime == True


bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

Quest_Session = Quest_Session()

# ON READY EVENT
# WHEN YOU START THE APPLICATION 

@bot.event
async def on_ready():
    print("Hello the bot is working i think?")

#region TRIAL COMMANDS !!!
# hello command just sends text xd
# add command, maths

@bot.command()
async def hello(ctx):
    await ctx.send("hello!!")

@bot.command()
async def add(ctx, *arr):
    result = 0
    for i in arr:
        result += float(i)
    await ctx.send(f"Result: {result}")

#endregion 

#region QUEST SESSION TIMER 
# command List : 
# quest - starts the quest session timer
# bs - starts a break time and logs its break duration
# be - ends the break time and prints the break duration (time since you did start the break and time now)
# end - stops the quest session timer

@bot.command()
async def quest(ctx, *arr):
    if Quest_Session.is_active:
        await ctx.send("A Quest session is already active!")
        return
    
    timeNow = ctx.message.created_at.timestamp()
    quest_name = ' '.join(arr)

    Quest_Session.Session_Activate()
    Quest_Session.start_time = timeNow
    Quest_Session.Set_QuestName(quest_name)

    readable_time = int(timeNow)
    await ctx.send(f"New Quest session of `{Quest_Session.quest_name}` has started at <t:{readable_time}:T>")

@bot.command()
async def bs(ctx):
    if not Quest_Session.is_active:
        await ctx.send("No Quest session is active!")
        return
    
    timeNow = ctx.message.created_at.timestamp()
    Quest_Session.has_breakTime = True
    Quest_Session.break_start = timeNow
    readable_time = int(timeNow)
    await ctx.send(f"Quest session break started at <t:{readable_time}:T>")

@bot.command()
async def be(ctx):
    if not Quest_Session.is_active:
        await ctx.send("No Break session to end!")
        return

    timeNow = ctx.message.created_at.timestamp()
    readable_endTime = int(timeNow)
    breakDuration = timeNow - Quest_Session.break_start
    Quest_Session.break_duration += breakDuration
    Quest_Session.break_start = 0
    readable_time = str(datetime.timedelta(seconds=breakDuration)).split('.')[0]
    await ctx.send(f"Quest Session break Ended at <t:{readable_endTime}:T> with {readable_time} duration.")


@bot.command()
async def end(ctx):
    if not Quest_Session.is_active:
        await ctx.send("No Quest session is active!")
        return
    
    end_time = ctx.message.created_at.timestamp()
    readable_endTime = int(end_time)
    Quest_Session.is_active = False
    
    total_duration = end_time - Quest_Session.start_time

    if not Quest_Session.had_breaks:
        readable_duration = str(datetime.timedelta(seconds=total_duration)).split('.')[0]
        await ctx.send(f"Quest session of {Quest_Session.quest_name} has ended at <t:{readable_endTime}:T> with {readable_duration} duration.")
        return

    QuestBreakDuration = Quest_Session.break_duration
    
    # if we end quest before ending break.
    if Quest_Session.is_on_break:
        QuestBreakDuration += end_time - Quest_Session.break_start
    
    if QuestBreakDuration != 0:
        net_duration = total_duration - QuestBreakDuration

        readable_duration = str(datetime.timedelta(seconds=net_duration)).split('.')[0]
        readable_break_duration = str(datetime.timedelta(seconds=QuestBreakDuration)).split('.')[0]
        
        await ctx.send(f"Quest session of {Quest_Session.quest_name} has ended at <t:{readable_endTime}:T> with {readable_duration} duration.\n" 
                        f"With Break time of {readable_break_duration} duration")
    else: 
        print("what on earth happened")

    Quest_Session.reset()

#endregion 
    
#region MAKING DATABASE FOR A GAME

@bot.command()
async def make_file(ctx, name):
    await ctx.send("hello!!")

#endregion
# RUN COMMAND

bot.run(BOT_TOKEN)

