
import discord
from wrappers.Firebase import FireBaseApi, firestore
from yt_dlp import YoutubeDL
from discord import app_commands
from discord.ext import commands
from constants import *
from embeds import *
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
        isEmptyServer = before.channel is not None and len(
            before.channel.members) == 1 and member.guild.voice_client is not None
        hasLeft = not member.bot and before.channel is not None and after.channel is None and len(
            before.channel.members) > 1

        collection = None
        if hasJoined:
            collection = Collections.WELCOME_COLLECTION.value
        elif isEmptyServer:
            await member.guild.voice_client.disconnect()
            return
        elif hasLeft:
            collection = Collections.OUTROS_COLLECTION.value

        if collection is not None and self.Firebase.documentExistsInCollection(collection, str(member.id)):
            documentKey = "intro_array" if collection == Collections.WELCOME_COLLECTION.value else "outro_array"
            channel = after.channel if collection == Collections.WELCOME_COLLECTION.value else before.channel
            if member.guild.voice_client is None:
                vc = await channel.connect()
            else:
                await member.guild.voice_client.move_to(channel)
                vc = member.guild.voice_client

            memberVoiceLines = self.Firebase.getElementFromCollection(
                collection, str(member.id))[documentKey]

            voiceLineUrl = self.Firebase.getAudioFile(choice(memberVoiceLines))
            if voiceLineUrl is None:
                return
            elif vc.is_playing():
                self.serverPlayers[member.guild.id].append(voiceLineUrl)
            else:
                await self.ExtractAndPlay(voiceLineUrl, vc, member.guild.id)

    @app_commands.command(name="upload", description="Upload a outro or an intro voiceline for a user.")
    @app_commands.describe(member="The member you wish to create a voiceline for", type="The type of voiceline you are creating")
    @app_commands.choices(type=[app_commands.Choice(name="Intro", value="intro"), app_commands.Choice(name="Outro", value="outro")])
    async def upload(self, interaction: discord.Interaction, member: discord.Member, type: app_commands.Choice[str], file: discord.Attachment):
        await interaction.response.defer()
        member_id = member.id
        voice_line_type = type.value
        content_type = file.content_type
        msg = None
        if content_type != "audio/mpeg":
            msg = await interaction.followup.send(invalid_usage_embed("File must be mp3!"))
        else:
            success, audioUrl = self.Firebase.uploadAudioFile(
                file.filename, file.url)

            if success:
                collectionName = Collections.WELCOME_COLLECTION.value if voice_line_type == "intro" else Collections.OUTROS_COLLECTION.value
                key = "intro_array" if voice_line_type == "intro" else "outro_array"
                memberDocument = str(member_id)
                data = {
                    key:  firestore.firestore.ArrayUnion([file.filename]),
                    "name": member.name
                }
                self.Firebase.insertElementInCollectionWithDefault(
                    collectionName, memberDocument, data)
                msg = await interaction.followup.send(embed=get_successful_file_upload_embed(member=member, type=voice_line_type, creatorMember=interaction.user, url=audioUrl))
            else:
                msg = await interaction.followup.send(embed=something_went_wrong_embed())

            await msg.delete(delay=600)

    def check_queue(self, vc: discord.VoiceClient, guild_id: int):
        if len(self.serverPlayers[guild_id]) > 0:
            next_song_up = self.serverPlayers[guild_id].popleft()
            self.bot.loop.create_task(
                self.ExtractAndPlay(next_song_up, vc, guild_id))

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
