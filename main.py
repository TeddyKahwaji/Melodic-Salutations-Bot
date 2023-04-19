import os
import discord
import logging
import asyncio
import ctypes
import ctypes.util
from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(intents=intents, command_prefix=".")


@bot.event
async def on_ready():
    print(f"Bot is ready to serve all {len(bot.guilds)} servers!")

@bot.tree.command(name='sync', description="Owner Only")
@commands.is_owner()
async def sync(interaction: discord.Interaction):
    await interaction.response.defer()
    await bot.tree.sync()
    await interaction.followup.send("Commands synced!")
    

async def load():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")


async def main():
    # Only run if on linux
    if os.name != 'nt':
        opus = ctypes.util.find_library('opus')
        discord.opus.load_opus(opus)
        if not discord.opus.is_loaded():
            raise RuntimeError("Opus failed to load")
    async with bot:
        await load()
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    DISCORD_TOKEN = os.environ["MELODY_DISCORD_TOKEN"]
    handler = logging.FileHandler(
        filename='discord.log', encoding='utf-8', mode='w')

    discord.utils.setup_logging(
        level=logging.INFO, root=False, handler=handler)

    asyncio.run(main())
