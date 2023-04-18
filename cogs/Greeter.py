
import discord
from wrappers.Firebase import FireBaseApi
from yt_dlp import YoutubeDL
from discord import app_commands
from discord.ext import commands
from constants import *
from collections import defaultdict, deque
from random import choice


class GreeterCog(commands.Cog, name="Greeter", description="Responsible for playing greetings and outros"):
    def __init__(self, bot):
        self.bot = bot
        self.serverPlayers = defaultdict(deque)
        self.Firebase = FireBaseApi()
        super().__init__()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        hasJoined = before.channel is None and after.channel is not None and not member.bot
        isEmptyServer = before.channel is not None and len(before.channel.members) == 1 and member.guild.voice_client is not None
        hasLeft = not member.bot and before.channel is not None and after.channel is None and len(before.channel.members) > 1

        
        performWelcomeIntro = None 
        if hasJoined:
            performWelcomeIntro = True 
        elif isEmptyServer:
            await member.guild.voice_client.disconnect()
            return 
        elif hasLeft: 
            performWelcomeIntro = False 
            
        if performWelcomeIntro is not None: 
            channel = after.channel if performWelcomeIntro else before.channel
            if member.guild.voice_client is None:
                vc =  await channel.connect() 
            else:
                await member.guild.voice_client.move_to(channel)
                vc = member.guild.voice_client
            
            collection = Collections.WELCOME_COLLECTION.value if performWelcomeIntro else Collections.OUTROS_COLLECTION.value
            documentKey = "intro_array" if performWelcomeIntro else "outro_array"
            memberVoiceLines = self.Firebase.getElementFromCollection(
                collection, str(member.id))[documentKey]
            
            voiceLineUrl = self.Firebase.getAudioFile(choice(memberVoiceLines))
            if vc.is_playing(): 
                self.serverPlayers[member.guild.id].append(voiceLineUrl)
            else: 
                await self.ExtractAndPlay(voiceLineUrl, vc, member.guild.id)
            

    def check_queue(self, vc: discord.VoiceClient, guild_id: int):
        if len(self.serverPlayers[guild_id]) > 0:
            next_song_up = self.serverPlayers[guild_id].popleft() 
            self.bot.loop.create_task(self.ExtractAndPlay(next_song_up, vc, guild_id))

    async def ExtractAndPlay(self, query: str, vc: discord.VoiceClient, guild_id: int) -> None:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(
                query, download=False)
            if 'entries' in info:
                info = info['entries'][0]

            url = info["url"]
            audio_source = discord.FFmpegPCMAudio(
                url, **FFMPEG_OPTIONS)
            vc.play(audio_source, after=lambda _: self.check_queue(vc,
                                                                guild_id))


async def setup(bot):
    await bot.add_cog(GreeterCog(bot))
