import os
from discord.ext import commands
import discord
from services.interface import ServicesProtocol
from services import Services
from UI.SelectionMenu import SelectionMenu
from UI.TableView import PaginatedTable
from UI.SimpleEmbed import SimpleEmbed

def setup_game_commands(bot, service: ServicesProtocol):
    @bot.command(name="update_db")
    async def update(ctx):
        result = service.settings_service.update_db_version()
        if not result.success:
            await ctx.send(result.message)
            return
        
        await ctx.send(f"Version Updated!")

    @bot.command(name="db_meta")
    async def database(ctx):
        result = service.settings_service.get_db_meta()

        if not result.success:
            await ctx.send(result.message)
            return
        
        build_embed = (
            SimpleEmbed(
                title = "Database Version",
                color = 0x00AE86
            )
        )
        build_embed.add_field(name="Version: ", value=result.data["version"])
        build_embed.add_field(name="Created: ", value=result.data["created_at"])
        build_embed.add_field(name="Last Modified: ", value=result.data["last_modified"])
        embed = build_embed.build()
        await ctx.send(embed=embed)

    @bot.command(name="addgame")
    async def add_game(ctx, *, game_name: str):
        result = service.game_service.create_game(ctx.channel.id, game_name)
        
        if not result.success:
            await ctx.send(result.message)
            return

        await ctx.send(result.message)

    @bot.command(name="update_pagination")
    async def add_game(ctx, *, pagination: int):
        result = service.settings_service.update_pagination(pagination)
        
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
        await ctx.send(f"Current game for this channel: {game['Game_Name']}")

    @bot.command(name="listgame")
    async def games_cmd(ctx):
        result = service.game_service.list_games()

        if not result.success:
            await ctx.send(result.message)
            return
        
        games = result.data
        
        game_menu = SelectionMenu(bot, setting_service=service.settings_service, items=games, title="🎮 Select a Game")

        async def on_game_select(interaction: discord.Interaction, selected_game, index):
            await interaction.response.edit_message(embed=game_menu.build_embed(), view=None)

            game_id = selected_game["id"]
            
            # Get Banner list on service
            banners = service.banner_service.get_banners(game_id)

            # DO VALIDATION HERE: CHECK IF THE GAME HAS BANNER LIST
            if not banners.success:
                await ctx.send(result.message)
                return
            
            banner_list = [
            {
                "name": f'ID: {b['Banner_ID']} | {b["Banner_Name"]} | At *{b["Current_Pity"]} pity*. |'
                        f'Last accessed: {b["Last_Updated"]}',
                "id": b["Banner_ID"]
            }
            for b in banners.data
        ]

            # Create banner menu based on selected game
            banner_menu = SelectionMenu(bot, setting_service=service.settings_service, items=banner_list, title=f"🎴 Select a Banner for {selected_game['name']}")

            async def on_banner_select(interaction: discord.Interaction, selected_banner, index):
                await interaction.response.edit_message(embed=banner_menu.build_embed(), view=None)
                
                banner_id = selected_banner["id"]

                # GET PULL HISTORY
                history = service.pull_service.get_banner_pulls(banner_id)
                
                # DO VALIDATION HERE: CHECK IF THE GAME HAS BANNER LIST
                if not history.success:
                    await ctx.send(history.message)
                    return

                # Create Table of Pull history
                view = PaginatedTable(
                    setting_service=service.settings_service,
                    items=history.data,
                    title="History",
                    timeout=60
                )

                message = await interaction.followup.send(
                    embed=view.build_embed(),
                    view=view
                )

                view.message = message

            banner_menu.set_callback(on_banner_select)
            await banner_menu.send(ctx.channel)

        game_menu.set_callback(on_game_select)
        await game_menu.send(ctx.channel)

    @bot.command(name="rename_game")
    async def rename_game(ctx, new_game: str):
        game = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game.message), 
                delete_after=5)        
        game_id = game.data['Game_ID']

        rename = service.game_service.rename_game(game_id, new_game)
        if not rename.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(rename.message), 
                delete_after=5)
        
        await ctx.send(rename.message)