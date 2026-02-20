import discord
from discord.ui import View, Button

ITEMS_PER_PAGE = 10 # pagination setting logic do here <----------


class PaginatedTable(View):
    def __init__(self, items, title="Table", page=0, timeout=120):
        super().__init__(timeout=timeout)
        self.items = items
        self.title = title
        self.page = page
        self.max_page = max(0, (len(items) - 1) // ITEMS_PER_PAGE)

        self._update_buttons()

    # ---------- EMBED BUILDER ----------

    def build_embed(self):
        embed = discord.Embed(title=self.title, color=discord.Color.blurple())

        start = self.page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_items = self.items[start:end]

        if not page_items:
            embed.description = "No data available."
            return embed

        table = ""
        headers = list(page_items[0].keys())

        header_line = " | ".join(headers)
        separator = "=" * len(header_line)

        table += header_line + "\n"
        table += separator + "\n"

        # Rows
        for item in page_items:
            row = [str(item.get(h, "")) for h in headers]
            table += " | ".join(row) + "\n"

        embed.description = f"```{table}```"
        embed.set_footer(text=f"Page {self.page + 1} / {self.max_page + 1}")

        return embed

    # ---------- BUTTON MANAGEMENT ----------

    def _update_buttons(self):
        # Access the decorator-created buttons by their callback name
        for item in self.children:
            if item.custom_id == "prev":
                item.disabled = self.page <= 0
            elif item.custom_id == "next":
                item.disabled = self.page >= self.max_page

    async def interaction_check(self, interaction: discord.Interaction):
        return True  # optionally restrict to original user

    async def on_timeout(self):
        self.clear_items()

        if hasattr(self, "message"):
            await self.message.edit(view=self)

    # ---------- INTERACTION HANDLER ----------

    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.secondary, custom_id="prev")
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.page < self.max_page:
            self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )
