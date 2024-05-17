
import discord
import asyncio
import pyshorteners
from datetime import datetime
from wrappers.Firebase import FireBaseApi, firestore
from yt_dlp import YoutubeDL
from discord import app_commands
from discord.ext import commands
from constants import *
from embeds import *
from views.PaginationList import PaginatedView
from views.DeleteVoiceline import DeleteVoicelineView
from collections import defaultdict, deque
import random


class GreeterCog(commands.Cog, name="Greeter", description="Responsible for playing greetings and outros"):
    def __init__(self, bot):
        self.bot = bot
        self.serverPlayers = defaultdict(deque)
        self.Firebase = FireBaseApi()
        self.UrlShortner = pyshorteners.Shortener()
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

        memberHasVoicelines = self.Firebase.documentExistsInCollection(
            collection, str(member.id))

        isBlacklisted = self.Firebase.documentExistsInCollection(
            Collections.BLACKLIST_COLLECTION.value, str(member.id))

        if collection is not None and memberHasVoicelines and not isBlacklisted:
            documentKey = "intro_array" if collection == Collections.WELCOME_COLLECTION.value else "outro_array"
            channel = after.channel if collection == Collections.WELCOME_COLLECTION.value else before.channel
            memberVoiceLines = self.Firebase.getElementFromCollection(
                collection, str(member.id))[documentKey]
            if len(memberVoiceLines) == 0:
                return
            elif member.guild.voice_client is None:
                vc = await channel.connect()
            else:
                await member.guild.voice_client.move_to(channel)
                vc = member.guild.voice_client

            memberVoiceLines.sort(
                key=lambda e: e["created_at"], reverse=True)
            chosen_track = random.choice(memberVoiceLines)
            voiceLineUrl, _ = await self.Firebase.getAudioFile(chosen_track["track_name"])
            if voiceLineUrl is None:
                return
            elif vc.is_playing():
                self.serverPlayers[member.guild.id].append(voiceLineUrl)
            else:
                await self.ExtractAndPlay(voiceLineUrl, vc, member.guild.id)

    @ app_commands.command(name="upload", description="Upload a voiceline for a user from your server")
    @ app_commands.describe(member="The member you wish to create a voiceline for", type="The type of voiceline you are creating", file="The mp3 file you wish to upload")
    @ app_commands.choices(type=[app_commands.Choice(name="Intro", value="intro"), app_commands.Choice(name="Outro", value="outro")])
    async def upload(self, interaction: discord.Interaction, member: discord.Member, type: app_commands.Choice[str], file: discord.Attachment):
        await interaction.response.defer()
        member_id = member.id
        voice_line_type = type.value
        content_type = file.content_type
        current_time = datetime.now()
        msg = None
        if content_type not in ["audio/mpeg", "audio/mp4", "application/zip"]:
            msg = await interaction.followup.send(embed=invalid_usage_embed("File must be an mp3 or m4a file!"))
        else:
            collectionName = Collections.WELCOME_COLLECTION.value if voice_line_type == "intro" else Collections.OUTROS_COLLECTION.value
            key = "intro_array" if voice_line_type == "intro" else "outro_array"
            memberDocument = str(member_id)

            memberVoicelines = self.Firebase.getElementFromCollection(
                collectionName, memberDocument)
            if content_type == "application/zip":
                success, results = await self.Firebase.uploadMassZip([] if memberVoicelines is None else memberVoicelines[key],  file, member)
                if not success:
                    msg = await interaction.followup.send(embed=something_went_wrong_embed("Sorry something went wrong processing the uploaded zip file :cry:"))
                    msg.delete(delay=30)
                    return
                for result in results:
                    data = {
                        key:  firestore.firestore.ArrayUnion([{"track_name": result["file"], "created_at": current_time, "added_by": interaction.user.id}]),
                        "name": member.name
                    }
                    if result["success"]:
                        result['url'] = self.UrlShortner.tinyurl.short(
                            result['url'])
                        self.Firebase.insertElementInCollectionWithDefault(
                            collectionName, memberDocument, data)

                msg = await interaction.followup.send(embed=get_successful_mass_upload_embed(member, voice_line_type, interaction.user, results))
            else:
                success, audioUrl, fileName = self.Firebase.uploadAudioFile(
                    file.url)
                if success:
                    data = {
                        key:  firestore.firestore.ArrayUnion([{"track_name": fileName, "created_at": current_time, "added_by": interaction.user.id}]),
                        "name": member.name
                    }
                    self.Firebase.insertElementInCollectionWithDefault(
                        collectionName, memberDocument, data)
                    msg = await interaction.followup.send(embed=get_successful_file_upload_embed(member=member, type=voice_line_type, creatorMember=interaction.user, url=audioUrl))
                else:
                    msg = await interaction.followup.send(embed=something_went_wrong_embed("Sorry an error occurred and I could not upload the inputted file"))

        await msg.delete(delay=600)

    @app_commands.command(name="voicelines", description="View the voicelines of a user from your server")
    @app_commands.describe(member="Member from your server", type="The type of voiceline you are viewing")
    @app_commands.choices(type=[app_commands.Choice(name="Intro", value="intro"), app_commands.Choice(name="Outro", value="outro")])
    @app_commands.checks.cooldown(1, 10)
    async def voicelines(self, interaction: discord.Interaction, member: discord.Member, type: app_commands.Choice[str]):
        await interaction.response.defer()
        documentKey = "intro_array" if type.value == "intro" else "outro_array"
        collection = Collections.WELCOME_COLLECTION.value if type.value == "intro" else Collections.OUTROS_COLLECTION.value
        try:
            memberDocument = self.Firebase.getElementFromCollection(
                collection, str(member.id))
            if memberDocument is None:
                msg = await interaction.followup.send(embed=no_data_for_member_embed(member, type.value))
                await msg.delete(delay=20)
                return

            memberVoiceLines = memberDocument[documentKey]
            results = await asyncio.gather(
                *[self.Firebase.getAudioFile(elem["track_name"]) for elem in memberVoiceLines])
            results = list(filter(lambda e: e[0] is not None, results))
            results = list(
                map(lambda e: (self.UrlShortner.tinyurl.short(e[0]), e[1]), results))
            if len(results) == 0:
                msg = await interaction.followup.send(embed=no_data_for_member_embed(member, type.value))
                await msg.delete(delay=20)
                return

            paginatedView = PaginatedView(member, type.value, results)
            await paginatedView.send(interaction)
        except:
            msg = await interaction.followup.send(embed=something_went_wrong_embed("Sorry something went wrong!"), ephemeral=True)
            await msg.delete(delay=20)

    @app_commands.command(name="blacklist", description="Add yourself to the blacklist to prevent me from greeting you")
    @app_commands.checks.cooldown(1, 10)
    async def blacklist(self, interaction: discord.Interaction):
        member_id = str(interaction.user.id)
        if self.Firebase.documentExistsInCollection(Collections.BLACKLIST_COLLECTION.value, member_id):
            await interaction.response.send_message(embed=already_on_blacklist_embed(interaction.user), ephemeral=True)
        else:
            data = {
                "name": interaction.user.name,
                "id": member_id
            }
            self.Firebase.insertElementInCollectionWithDefault(
                Collections.BLACKLIST_COLLECTION.value, member_id, data)
            await interaction.response.send_message(embed=added_to_blacklist_embed(interaction.user), ephemeral=True)

    @app_commands.command(name="whitelist", description="Remove yourself from the blacklist to receive greetings from me")
    @app_commands.checks.cooldown(1, 10)
    async def whitelist(self, interaction: discord.Interaction):
        member_id = str(interaction.user.id)
        if not self.Firebase.documentExistsInCollection(Collections.BLACKLIST_COLLECTION.value, member_id):
            await interaction.response.send_message(embed=not_on_blacklist(interaction.user), ephemeral=True)
        else:
            self.Firebase.removeDocumentFromCollection(
                Collections.BLACKLIST_COLLECTION.value, member_id)

            await interaction.response.send_message(embed=removed_from_blacklist_embed(interaction.user), ephemeral=True)

    @app_commands.command(name="delete", description="Deletes voicelines for a given member")
    @app_commands.describe(member="Member from your server", type="The type of voiceline you are viewing")
    @app_commands.choices(type=[app_commands.Choice(name="Intro", value="intro"), app_commands.Choice(name="Outro", value="outro")])
    @app_commands.checks.cooldown(1, 10)
    async def delete(self, interaction: discord.Interaction, member: discord.Member, type: app_commands.Choice[str]):
        await interaction.response.defer()
        voice_line_type = type.value
        collectionName = Collections.WELCOME_COLLECTION.value if voice_line_type == "intro" else Collections.OUTROS_COLLECTION.value
        memberDocument = str(member.id)
        key = "intro_array" if voice_line_type == "intro" else "outro_array"
        memberVoicelines = self.Firebase.getElementFromCollection(
            collectionName, memberDocument)
        msg = None
        if memberVoicelines is None or len(memberVoicelines[key]) == 0:
            msg = await interaction.followup.send(embed=no_data_for_member_embed(member, voice_line_type))
            await msg.delete(delay=180)
        else:
            deleteView = DeleteVoicelineView(memberVoicelines[key], member, voice_line_type, interaction.user, delete_key=lambda fileName: self.Firebase.deleteAudioFile(
                fileName), insert_key=lambda e: self.Firebase.insertElementInCollectionWithDefault(collectionName, memberDocument, e), member_voicelines=memberVoicelines[key])
            await deleteView.send(interaction)

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
