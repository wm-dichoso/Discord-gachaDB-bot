import discord
from discord.ext import commands
from typing import List, Union, Callable

class SelectionMenu(discord.ui.View):
    def __init__(
        self,
        bot: commands.Bot,
        items: List[Union[str, dict]],
        title: str = "Select an item",
        items_per_page: int = 10,
        timeout: int = None
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.items = items
        self.title = title
        self.items_per_page = items_per_page
        self.on_select: Callable = None
        self.current_page = 0

        # Buttons
        self.previous_button = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary)
        self.next_button = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary)

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        # Add nav buttons
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        # Add item buttons dynamically in build_buttons()
        self.build_buttons()

    def build_buttons(self):
        # Remove old item buttons except navigation
        self.clear_items()
        
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        page_items = self.items[start_index:end_index]

        for idx, item in enumerate(page_items):
            real_index = start_index + idx
            label = str(idx + 1)
            button = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.primary,
                custom_id=f"select_{real_index}"
            )
            async def callback(interaction: discord.Interaction, index=real_index):
                selected_item = self.items[index]
                if self.on_select:
                    await self.on_select(interaction, selected_item, index)
            button.callback = callback
            self.add_item(button)
        
        # Re-add nav buttons
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    def build_embed(self) -> discord.Embed:
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        page_items = self.items[start_index:end_index]

        description = ""
        for idx, item in enumerate(page_items):
            if isinstance(item, str):
                description += f"{idx + 1}. {item}\n"
            elif isinstance(item, dict) and "name" in item:
                description += f"{idx + 1}. {item['name']}\n"
            else:
                description += f"{idx + 1}. Item\n"

        total_pages = (len(self.items) - 1) // self.items_per_page + 1
        embed = discord.Embed(
            title=self.title,
            description=description,
            color=0x00AE86
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{total_pages}")
        return embed

    async def send(self, channel: discord.abc.Messageable):
        embed = self.build_embed()
        return await channel.send(embed=embed, view=self)

    def set_callback(self, callback: Callable):
        self.on_select = callback

    # Pagination handlers
    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.build_buttons()
            await interaction.response.edit_message(embed=self.build_embed(), view=self)
        else:
            await interaction.response.defer()  # nothing happens if already at first page

    async def next_page(self, interaction: discord.Interaction):
        total_pages = (len(self.items) - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.build_buttons()
            await interaction.response.edit_message(embed=self.build_embed(), view=self)
        else:
            await interaction.response.defer()  # nothing happens if already at last page
