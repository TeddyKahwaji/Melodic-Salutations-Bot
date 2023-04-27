from discord import Embed, Colour, Member
from constants import Gifs, Images, COMMANDS_TO_DESCRIPTION


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


def get_successful_mass_upload_embed(member: Member, type: str, creatorMember: Member, results: list[dict]) -> Embed:
    embed = Embed(title=f"",
                  colour=0x67e9ff
                  )
    successful_voicelines = 1

    successful_fields = list(filter(lambda e: e["success"], results))
    failed_fields = list(filter(lambda e: not e["success"], results))

    if len(failed_fields) == 0 and len(successful_fields) == 0:
        return invalid_usage_embed("You provided an empty zip!")

    if len(successful_fields) > 0:
        embed.add_field(name="**Successfully processed voicelines 😊:**",
                        value="", inline=False)
    for result in successful_fields:
        embed.add_field(
            name="", value=f"{member.name}'s new [Voiceline #{successful_voicelines}]({result['url']}) 🎤!", inline=False)
        successful_voicelines += 1

    if len(failed_fields) > 0:
        embed.add_field(name="**Failed to process voicelines 😥:**",
                        value="", inline=False)
    for result in failed_fields:
        embed.add_field(
            name="", value=f"`Unforunately {result['file']} could not be uploaded because {result['error_message']}`", inline=False)
    embed.title = f"🎤 {successful_voicelines-1} voiceline {type}s successfully created 🎤"
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


def already_on_blacklist_embed(member: Member) -> Embed:
    embed = Embed(
        title=f"{member.name} is already on the blacklist!", color=Colour.dark_blue())

    embed.add_field(
        name="", value="To remove yourself from the blacklist, use `/whitelist`")
    embed.set_thumbnail(url=member.avatar.url)

    return embed


def not_on_blacklist(member: Member) -> Embed:
    embed = Embed(
        title=f"{member.name} is not on the blacklist!", color=Colour.dark_blue())

    embed.add_field(
        name="", value="To add yourself to the blacklist, use `/blacklist`")
    embed.set_thumbnail(url=member.avatar.url)

    return embed


def added_to_blacklist_embed(member: Member) -> Embed:
    embed = Embed(
        title=f"{member.name} has been added to the blacklist!", color=0x67e9ff)
    embed.add_field(
        name="", value="You will no longer be greeted with a voiceline when joining a voice channel, if you'd like to undo this use `/whitelist`")

    embed.set_thumbnail(url=member.avatar.url)
    return embed


def removed_from_blacklist_embed(member: Member) -> Embed:
    embed = Embed(
        title=f"{member.name} has been removed from the blacklist!", color=0x67e9ff)

    embed.add_field(
        name="", value="You will now be greeted with voicelines, if you'd like to undo this use `/blacklist`")

    embed.set_thumbnail(url=member.avatar.url)
    return embed


def select_delete_view_embed(member: Member) -> Embed:
    embed = Embed(
        title=f"Please select the following voicelines you'd like to delete for {member.name}", color=0x67e9ff)

    embed.add_field(
        name="", value="Please note that deletion is permanent and cannot be undone")

    embed.set_thumbnail(url=member.avatar.url)
    return embed


def waiting_embed() -> Embed:
    embed = Embed(
        title="Please wait while your deletion job is completed", color=0x67e9ff)
    embed.set_thumbnail(url=Images.WAITING_ROBOT.value)
    return embed


def deletion_completed_embed(results, requester_member, member) -> Embed:
    embed = Embed(
        title=f"{len(results)} voicelines deleted for {member.name}", color=0x67e9ff)

    embed.add_field(name="**Successfully deleted voicelines 😊:**",
                    value="", inline=False)
    for _, filename in results:
        embed.add_field(name="", value=f"`{filename}`", inline=False)

    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(
        text=f"Deleted by: {requester_member.name}", icon_url=requester_member.avatar.url)
    return embed


def get_help_menu_embed():
    help_menu = Embed(
        title="**🤖 Melodic Saluation's Help Page 👋**",
        description=f"I only supports `/` commands, to view available commands use `/` followed by the desired command",
        colour=0x67e9ff
    )

    for command, description in COMMANDS_TO_DESCRIPTION.items():
        help_menu.add_field(name=f"**{command}**", value=f"``{description}``")

    return help_menu
