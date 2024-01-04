import discord
import asyncio
from firebase_admin import firestore
from embeds import *


class DeleteVoicelineView(discord.ui.View):
    def __init__(self, voice_lines: list[str], member: discord.Member, voice_line_type: str, requester_member, delete_key, insert_key, member_voicelines):
        self.member = member
        self.voice_lines = voice_lines
        self.voice_line_type = voice_line_type
        self.delete_key = delete_key
        self.insert_key = insert_key
        self.requester_member = requester_member
        self.member_voicelines = member_voicelines
        super().__init__()

    async def send(self, interaction: discord.Interaction):
        self.selection_wheel.options = [discord.SelectOption(
            label=f"{self.member.name}'s #{i+1}", value=voiceline["track_name"]) for i, voiceline in enumerate(self.voice_lines[:25])]
        self.selection_wheel.max_values = len(self.selection_wheel.options)
        self.message = await interaction.followup.send(view=self)
        await self.message.delete(delay=600)
        await self.update_message()

    async def update_message(self):
        await self.message.edit(embed=select_delete_view_embed(self.member))

    @discord.ui.select(placeholder="Select which voicelines you'd like to delete", options=[discord.SelectOption(label='Temp', value='Temp')], min_values=1)
    async def selection_wheel(self, interaction, select: discord.Interaction):
        await interaction.response.defer()
        selected_results = select.values
        await self.message.edit(view=None, embed=waiting_embed())
        results = await asyncio.gather(
            *[self.delete_key(selected_audio_file) for selected_audio_file in selected_results])
        results = list(filter(lambda success: success[0], results))
        if len(results) == 0:
            await self.message.edit(view=None, embed=something_went_wrong_embed("Something went wrong in the deletion process"))
            await self.message.delete(delay=180)
            return

        fileNames = set(filename for _, filename in results)

        key = "intro_array" if self.voice_line_type == "intro" else "outro_array"
        data = {
            key:  [voiceline for voiceline in self.member_voicelines if voiceline['track_name'] not in fileNames],
            "name": self.member.name
        }
        self.insert_key(data)
        await self.message.edit(view=None, embed=deletion_completed_embed(results, self.requester_member, self.member))
        await self.message.delete(delay=600)
