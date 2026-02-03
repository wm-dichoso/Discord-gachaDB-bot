import discord

class SimpleEmbed:
    def __init__(
        self,
        title: str = None,
        description: str = None,
        color: discord.Color = discord.Color.blurple()
    ):
        self.embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

    def add_field(self, name: str, value: str, inline: bool = False):
        self.embed.add_field(name=name, value=value, inline=inline)
        return self  # allows chaining

    def set_footer(self, text: str):
        self.embed.set_footer(text=text)
        return self

    def set_author(self, name: str, icon_url: str = None):
        self.embed.set_author(name=name, icon_url=icon_url)
        return self

    def set_thumbnail(self, url: str):
        self.embed.set_thumbnail(url=url)
        return self

    def set_image(self, url: str):
        self.embed.set_image(url=url)
        return self

    def build(self) -> discord.Embed:
        return self.embed
