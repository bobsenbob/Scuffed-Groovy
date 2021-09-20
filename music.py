import discord
from discord.ext import commands
import youtube_dl
import queue
import asyncio
class music(commands.Cog):
  def __init__(self, client):
    self.client = client
  playlist = queue.Queue()
  playlist_info = queue.Queue()
  @commands.command()
  async def join(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You're not in a voice channel")
      return False
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
  @commands.command()
  async def disconnect(self, ctx):
    if ctx.voice_client is None:
      return
    await ctx.voice_client.disconnect()
    
      

  @commands.command()
  async def play(self, ctx, url):
    
    await self.join(ctx)
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(url, download = False)
      duration = info['duration']
      print(duration)
      print('\n')
      url2 = info['formats'][0]['url']
      source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
      self.playlist.put((source, url))
      self.playlist_info.put(info)
    if self.playlist.qsize() > 0:
      await ctx.send("Added to the queue: " + str(url))
    vc = ctx.voice_client
    if vc.is_playing() and not vc.is_paused():
        return
    while not self.playlist.empty():
      print("items in queue: " + str(self.playlist.qsize()))
      source = self.playlist.get()
      vc.play(source[0])
      playing_message = await ctx.send("now playing: " + str(source[1]))
      while vc.is_playing() and not vc.is_paused():
        await asyncio.sleep(1)
      await playing_message.delete()
  @commands.command()
  async def pause(self, ctx):
    ctx.voice_client.pause()
    await ctx.send("Paused")
  @commands.command()
  async def resume(self,ctx):
    ctx.voice_client.resume()
    await ctx.send("Resumed")
  @commands.command()
  async def stop(self,ctx):
    ctx.voice_client.stop()
    await ctx.send("Stopped")
  @commands.command()
  async def left(self,ctx):
    await ctx.send("Items left: " + str(self.playlist.qsize()))
  @commands.command()
  async def skip(self,ctx):
    ctx.voice_client.stop()
    await self.play(self, ctx)
  @commands.command()
  async def display(self,ctx):
    block_message = ""
    for i in range(min(self.playlist_info.qsize(), 5)):
      info = self.playlist_info.get()
      self.playlist_info.put(info)
      dur = str(info['duration']//60) + ":"
      if info['duration'] % 60 < 10:
        dur += "0"
      dur += str(info['duration'] % 60)
      addition = " " + str(i + 1) + ". " + info['title'] + " [" + dur + "]\n"
      if len(block_message) + len(addition) > 3900:
        block_message += "..."
        break
      block_message = block_message + addition
    print(block_message)
    if (self.playlist_info.qsize() > 0):
      await ctx.send("```ini\n" + block_message + "\n```")
    else:
      await ctx.send("No songs in the queue!")
def setup(client):
  client.add_cog(music(client))