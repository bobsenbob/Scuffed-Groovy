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
  
  channel_id = channel.id
  for i in client.get_all_channels():
    print(i.name)
    print(i.guild)
    print(i.data)
      


@client.command()
async def test2(ctx, *args):
  await ctx.send(' '.join(args))
client.run('ODg5MzgxODY3MDEzNDI3MjAw.YUgbaQ.z4hcy0lfvTx0Js_OYpB3ZKRMorE')
#ODg5MDEzNjQ4NTI0MTkzODAy.YUbEeg.zdKdBt9ZzlRlBjY3OIJtor3JCsY Encourage Bot
#ODg5MzgxODY3MDEzNDI3MjAw.YUgbaQ.z4hcy0lfvTx0Js_OYpB3ZKRMorE Scuffier Groovy