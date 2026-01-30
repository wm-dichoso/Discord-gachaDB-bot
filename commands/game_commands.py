from discord.ext import commands
import discord
from services.interface import ServicesProtocol
from services import Services
from UI.SelectionMenu import SelectionMenu

def setup_game_commands(bot, service: ServicesProtocol):

    @bot.command(name="addgame")
    async def add_game(ctx, *, game_name: str):
        result = service.game_service.create_game(ctx.channel.id, game_name)
        
        if not result.success:
            await ctx.send(result.message)
            return

        await ctx.send(result.message)

    @bot.command(name="game")
    async def get_game(ctx):
        result = service.game_service.get_game_for_channel(ctx.channel.id)

        if not result.success:
            await ctx.send(result.message)
            return

        game = result.data
        await ctx.send(f"Current game: {game['name']}")

    @bot.command()
    async def list_game(ctx):
        result = service.game_service.list_games()

        if not result.success:
            await ctx.send(result.message)
            return
        
        game_names = [game.get("Game_Name") for game in result.data if game.get("Game_Name")]
        game_list = ", ".join(game_names)


        await ctx.send(f"Current game: {game_list}")


    @bot.command(name="listgame")
    async def games_cmd(ctx):
        result = service.game_service.list_games()

        if not result.success:
            await ctx.send(result.message)
            return
        
        games = result.data

        banners = {
            1: [{"name": "Banner A1", "id": 101}, {"name": "Banner A2", "id": 102}],
            2: [{"name": "Banner B1", "id": 201}, {"name": "Banner B2", "id": 202}],
            3: [{"name": "Banner C1", "id": 301}, {"name": "Banner C2", "id": 302}],
        }
        
        game_menu = SelectionMenu(bot, items=games, title="🎮 Select a Game")

        async def on_game_select(interaction: discord.Interaction, selected_game, index):
            # Remove buttons from game menu
            await interaction.response.edit_message(embed=game_menu.build_embed(), view=None)

            # Create banner menu based on selected game
            # DO VALIDATION HERE: CHECK IF THE GAME HAS BANNER LIST
            game_id = selected_game["id"]
            banner_list = service.banner_service.get_banners(game_id)

            banner_menu = SelectionMenu(bot, items=banners[game_id], title=f"🎴 Select a Banner for {selected_game['name']}")

            async def on_banner_select(interaction: discord.Interaction, selected_banner, index):
                # Remove buttons from banner menu
                await interaction.response.edit_message(embed=banner_menu.build_embed(), view=None)
                # Reply to user
                await interaction.followup.send(
                    f"You selected **{selected_game['name']}** → **{selected_banner['name']}**!",
                    ephemeral=True
                )

            banner_menu.set_callback(on_banner_select)
            await banner_menu.send(ctx.channel)

        game_menu.set_callback(on_game_select)
        await game_menu.send(ctx.channel)
