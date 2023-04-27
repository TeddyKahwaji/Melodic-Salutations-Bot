import discord


class PaginatedView(discord.ui.View):
    current_page: int = 1
    sep: int = 5

    def __init__(self,  member: discord.Member, type: str, data: list[str]):
        self.data = data
        self.member = member
        self.type = type
        super().__init__(timeout=None)

    async def send(self, interaction: discord.Interaction):
        self.message = await interaction.followup.send(view=self)
        await self.update_message()
        await self.message.delete(delay=600)

    def create_embed(self, data):
        embed = discord.Embed(title=f"{self.member.name}'s voiceline {self.type}s",
                              colour=0x67e9ff)
        embed.set_thumbnail(url=self.member.avatar.url)
        if len(data) == 0:
            self.current_page = 1
            data = self.get_current_page_data()

        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        for item in data:
            embed.add_field(name="",
                            value=f"`{from_item+1}:` [Voiceline]({item})", inline=False)
            from_item += 1
        embed.set_footer(
            text=f"Page {self.current_page} / {int(len(self.data) / self.sep) + 1}", icon_url=self.member.avatar.url)
        return embed

    async def update_message(self):
        data = self.get_current_page_data()

        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == int(len(self.data) / self.sep) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    def get_current_page_data(self):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == int(len(self.data) / self.sep) + 1:
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        return self.data[from_item:until_item]

    @discord.ui.button(label="|<",
                       style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1

        await self.update_message()

    @discord.ui.button(label="<",
                       style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.update_message()

    @discord.ui.button(label=">",
                       style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        await self.update_message()

    @discord.ui.button(label=">|",
                       style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = int(len(self.data) / self.sep) + 1
        await self.update_message()
