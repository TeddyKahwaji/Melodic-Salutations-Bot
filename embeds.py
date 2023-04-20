from discord import Embed, Colour, Member
from constants import Gifs


def get_successful_file_upload_embed(member: Member, type: str, creatorMember: Member, url: str) -> Embed:
    embed = Embed(title=f"🎤 Voiceline {type} successfully created 🎤",
                  colour=0x67e9ff
                  )

    embed.add_field(
        name=f"", value=f"{member.name}'s new [Voiceline]({url}) 🎤!")
    embed.set_thumbnail(url=member.avatar.url)

    embed.set_footer(
        text=f"Created by: {creatorMember.name}", icon_url=creatorMember.avatar.url)

    return embed


def no_data_for_member_embed(member: Member, type: str) -> Embed:
    embed = Embed(
        title=f"There are no {type} voicelines for {member.name}", color=Colour.dark_blue())
    embed.add_field(
        name="", value=f"Upload a voiceline for **{member.name}** with `/upload`")
    embed.set_thumbnail(url=Gifs.ROBOT_SEARCHING.value)
    return embed


def something_went_wrong_embed(message) -> Embed:
    embed = Embed(title="Oops something went wrong!", colour=Colour.dark_red())
    embed.add_field(
        name=f"`{message}`", value="")
    embed.set_thumbnail(url=Gifs.BROKEN_ROBOT.value)

    return embed


def invalid_usage_embed(msg: str) -> Embed:
    invalid_embed = Embed(
        title="❌ **Invalid usage**",
        description=f"`{msg}`",
        colour=Colour.dark_red()
    )
    invalid_embed.set_thumbnail(url=Gifs.INVALID_USAGE.value)
    return invalid_embed
