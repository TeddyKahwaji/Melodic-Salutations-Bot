import os
import discord
import logging
import asyncio
import ctypes
import ctypes.util
from embeds import *
from discord.ext import commands
from discord import app_commands


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(intents=intents, command_prefix=".")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("/help"))
    print(f"Bot is ready to serve all {len(bot.guilds)} servers!")


@bot.tree.command(name="ping", description="View bot's latency")
async def ping(interaction: discord.Interaction):
    latency = round(interaction.client.latency * 1000)
    embed_color = None
    if latency <= 50:
        embed_color = 0x44ff44
    elif latency <= 100:
        embed_color = 0xffd000
    elif latency <= 200:
        embed_color = 0xff6600
    else:
        embed_color = 0x990000

    embed = discord.Embed(
        title="PING", description=f":ping_pong: My ping is **{latency}** ms.", color=embed_color)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="help", description="Displays the command menu")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(embed=get_help_menu_embed(), ephemeral=True)


async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    error_log_channel_id = 1094732412845576266
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = invalid_usage_embed(error)
        embed.set_thumbnail(url=Gifs.COOLDOWN.value)
        await interaction.response.send_message(embed=embed, delete_after=error.retry_after, ephemeral=True)

    error_log_channel = await interaction.client.fetch_channel(error_log_channel_id)
    errored_command = error.command.name
    errored_guild = interaction.guild
    await error_log_channel.send(embed=get_error_log_embed(errored_command, errored_guild, error))


@bot.tree.command(
    name="reload",
    description="Reloads the cog files. Use this to deploy changes to the bot"
)
@commands.is_owner()
async def reload(interaction: discord.Interaction):
    if not await bot.is_owner(interaction.user):
        return
    await interaction.response.send_message("Reloaded cogs!", ephemeral=True)
    await load(reload=True)


@bot.tree.command(name='sync', description="Owner Only")
@commands.is_owner()
async def sync(interaction: discord.Interaction):
    if not await bot.is_owner(interaction.user):
        return
    await interaction.response.send_message("Commands synced!", ephemeral=True)
    await bot.wait_until_ready()
    await bot.tree.sync()


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

    bot.tree.on_error = on_tree_error
    asyncio.run(main())
