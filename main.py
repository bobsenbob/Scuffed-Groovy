import discord
from discord.ext import commands
import music
client = commands.Bot(command_prefix = '-', intents = discord.Intents.all())
cogs = [music]
for i in range(len(cogs)):
  cogs[i].setup(client)
import logging
logging.basicConfig(level=logging.INFO)

  
@client.command()
async def test(ctx):
  for i in client.get_all_channels():
    print(i.name)
    print(i.guild)
    print(i.data)
      


@client.command()
async def test2(ctx, *args):
  await ctx.send(' '.join(args))
token = ""
client.run(token)
