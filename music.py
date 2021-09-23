import discord
from discord.ext import commands
import youtube_dl
import random
from collections import deque
import asyncio
#889013444005740568 is General voice channel
class loopqueue:
  #1 is no loop, 2 is loop song, 3 is loop entire queue

  def __init__(self,lp):
    self.loop = lp
    self.line = deque()
  def get(self):
    return self.line.popleft()
  def gettail(self):
    return self.line.pop()
  def put(self, value):
    self.line.append(value)
  def puthead(self, value):
    self.line.appendleft(value)
  def peek(self, index = 0):
    return self.line[index]
  def peektail(self):
    return self.line[-1]
  def qsize(self):
    return len(self.line)
  def empty(self):
    return self.qsize() == 0
    
class music(commands.Cog):
  musicqueue = loopqueue(1)
  #stores the source music file for each song
  #left is head and must be noted, right is tail and is implicit
  #put(left), get(left)
  musicqueue_info = loopqueue(1)
  playing = False
  #stores the 'info' for each song
  def __init__(self, client):
    self.client = client

  #https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-pass-a-coroutine-to-the-player-s-after-function
  def my_after(self, ctx):
    print("after 1")
    fut = asyncio.run_coroutine_threadsafe(self.begin(ctx), self.client.loop)
    print("after 2")
    try:
      print("after 31")
      fut.result()
      print("after 32")
    except:
      print("after 41")
      pass

  async def begin(self, ctx):
    
    if ctx.author.voice is None:
      await self.join(ctx, 'General')
    else:
      await self.join(ctx)
    if self.musicqueue.qsize() == 0:
      return;
    vc = ctx.voice_client
    if vc.is_playing() and not vc.is_paused():
      return
    print("items in queue: " + str(self.musicqueue.qsize()))

    source = self.musicqueue.peek()
    details = self.musicqueue_info.peek()
    #change music_info queue to list so that you can peek at the first 5
    print('check 1')
    while (ctx.voice_client is None):
      await asyncio.sleep(1)
    print('check 2')
    print('check 3')
    playing_message = await ctx.send("now playing: " + str(details['webpage_url']))
    self.musicqueue.get()
    self.musicqueue_info.get()
    vc.play(source[0], after = lambda e: self.my_after(ctx))
    print('check 4')
    
      
  
  @commands.command()
  async def join(self, ctx, channel = None):
    if channel == None:
      if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel")
        return False
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await ctx.voice_client.move_to(voice_channel)
    else:
      if channel in [x.name for x in self.client.get_all_channels() if str(x.type) == 'voice']:
        voice_channel = discord.utils.get(ctx.guild.channels, name=channel)
        if ctx.voice_client is None:
          await voice_channel.connect()
        else:
          await ctx.voice_client.move_to(voice_channel)
      else:
        await ctx.send("No voice channel called " + channel + " exists!")

  @commands.command()
  async def disconnect(self, ctx):
    if ctx.voice_client is None:
      return
    await ctx.voice_client.disconnect()
  
  @commands.command()
  async def play(self, ctx, url, index = 1, isFirst = True, playlist_length = -1):
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    is_playlist = "playlist" in url
    if not is_playlist:
      YDL_OPTIONS = {'format': 'bestaudio'}
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download = False)
        #duration = info['duration']
        #print(duration)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
        self.musicqueue.put((source, url))
        self.musicqueue_info.put(info)
        if self.musicqueue.qsize() > 0:
          await ctx.send("Added to the queue: " + str(url))
        await self.begin(ctx)
    else:
      
      if isFirst:
        YDL_OPTIONS = {'extract_flat': 'in_playlist'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          playlist_info = ydl.extract_info(url, download = False)
        if playlist_length < 0:
          playlist_length = len(playlist_info['entries']) + 1 - index
      print("starting loop")
      YDL_OPTIONS = {'format': 'bestaudio', 'playlist_items': str(index)}
      print("index: " + str(index))
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download = False)

        url2 = info['entries'][0]['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
        self.musicqueue.put((source, url))
        self.musicqueue_info.put(info['entries'][0])
        #print(self.musicqueue_info.peektail())
      progress = await ctx.send("queueing: " + self.musicqueue_info.peektail()['webpage_url'])
      await progress.delete()
      progress = await ctx.send("\n" + str(index) + " out of " + str(playlist_length) + " queued")

      #need to fix deletion of 'x out of y queued' messages
      index += 1
      if (index <= playlist_length):
        await asyncio.gather(self.begin(ctx), self.play(ctx, url, index, False, playlist_length))
      else:
        await self.begin(ctx)
    


    
    
    
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
    await ctx.send("Items left: " + str(self.musicqueue.qsize()))

  @commands.command()
  async def skip(self,ctx):
    ctx.voice_client.stop()
  
  @commands.command()
  async def display(self,ctx):
    block_message = ""
    for i in range(min((self.musicqueue_info.qsize()), 5)):
      info = self.musicqueue_info.peek(i)
      dur = str(info['duration']//60) + ":"
      if info['duration'] % 60 < 10:
        dur += "0"
      dur += str(info['duration'] % 60)
      addition = " " + str(i + 1) + ". " + info['title'] + " [" + dur + "]\n"
      if len(block_message) + len(addition) > 3900 or self.musicqueue_info.qsize() > 5:
        block_message += "..."
        break
      block_message = block_message + addition
    print(block_message)
    if (self.musicqueue_info.qsize() > 0):
      await ctx.send("```ini\n" + block_message + "\n```")
    else:
      await ctx.send("No songs in the queue!")

  @commands.command()
  async def loopsong(self,ctx):
    self.musicqueue.loop = 2

  @commands.command()
  async def loop(self,ctx):  
    self.musicqueue.loop = 3

  @commands.command()
  async def shuffle(self,ctx):
    #empty deque into list at random indices then refill deque
    #change to nly shuffle indices 1...n
    index_list = []
    for i in range(self.musicqueue.qsize()):
      index_list.append(i)
    random.shuffle(index_list)
  
    for i in index_list: 
      self.musicqueue.put(self.musicqueue.line[i])
      self.musicqueue_info.put(self.musicqueue_info.line[i])
    for i in index_list:
      self.musicqueue.get()
      self.musicqueue_info.get()
    
def setup(client):
  client.add_cog(music(client))