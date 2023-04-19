from discord import Embed, Colour, Member
from constants import Gifs


def get_successful_file_upload_embed(member: Member, type: str, creatorMember: Member, url: str) -> Embed:
    embed = Embed(title=f"🎤 Voiceline {type} successfully created 🎤",
                  colour=Colour.dark_green()
                  )

    embed.add_field(
        name=f"", value=f"{member.name}'s new [Voiceline]({url}) 🎤!")
    embed.set_thumbnail(url=member.avatar.url)

    embed.set_footer(
        text=f"Created by: {creatorMember.name}", icon_url=creatorMember.avatar.url)

    return embed


def something_went_wrong_embed() -> Embed:
    embed = Embed(title="Oops something went wrong!", colour=Colour.dark_red())
    embed.add_field(
        name="`Sorry an error occured and I could not upload the inputted file`", value="")
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
