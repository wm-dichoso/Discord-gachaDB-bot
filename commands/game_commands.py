import os
from discord.ext import commands
import discord
from services.interface import ServicesProtocol
from services import Services
from UI.SelectionMenu import SelectionMenu
from UI.TableView import PaginatedTable
from UI.SimpleEmbed import SimpleEmbed

def parse_csv_args(arg_string: str, expected: int):
    parts = [p.strip() for p in arg_string.split(",")]
    if len(parts) != expected:
        raise ValueError
    return parts

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
            await ctx.send("⚠ SERVICE ERROR:"+ str(result.message))
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

    # currency services
    @bot.command(name="cur")
    async def get_currency(ctx):
        game = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game.message), 
                delete_after=20)        
        game_id = game.data['Game_ID']
        game_name = game.data['Game_Name']

        currency = service.currency_service.get_game_currency_info(game_id)
        if not currency.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(currency.message), 
                delete_after=20)
        
        build_embed = (
            SimpleEmbed(
                title = str(game_name),
                color = 0x00AE86
            )
        )
        build_embed.add_field(name="Game_Currency: ", value=currency.data["Game_Currency"])
        build_embed.add_field(name="Pull Tokens Available: ", value=currency.data["Pull_Tokens"])
        build_embed.add_field(name="Current Goal: ", value=currency.data["Goal"])
        embed = build_embed.build()
        await ctx.send(embed=embed)

    @bot.command(name="install-cur")
    async def install_currency(ctx, currency, pull_token):
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        currency_install = service.currency_service.install_game_currency(game_id, currency, pull_token)
        if not currency_install.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(currency_install.message), 
                delete_after=20)

        await ctx.send(currency_install.message)

    @bot.command(name="goal")
    async def set_currency_goal(ctx, goal: int):
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        currency_goal = service.currency_service.set_game_currency_goal(game_id, goal)
        if not currency_goal.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(currency_goal.message), 
                delete_after=20)

        await ctx.send(currency_goal.message)
        
    @bot.command(name="done_goal")
    async def unset_currency_goal(ctx):
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        currency_goal = service.currency_service.unset_game_currency_goal(game_id)
        if not currency_goal.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(currency_goal.message), 
                delete_after=20)

        await ctx.send(currency_goal.message)
        
    @bot.command(name="cur-amount")
    async def currency_update_amount(ctx, *, args: str):
        try:
            amount, reason = parse_csv_args(args, 2)            
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.cur-amount* `New Amount`, `Reason`", 
                delete_after=20)
            return
        
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        amount_update = service.currency_service.update_currency_amount(game_id, amount, reason)
        if not amount_update.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(amount_update.message), 
                delete_after=20)
        
        if amount_update.data is not None:
            build_embed = (
                SimpleEmbed(
                    title = "Goal Reached",
                    color = 0x00AE86
                )
            )
            embed_title = "Currency Goal of "+str(amount_update.data['Goal'])
            content = "is now Reached"
            build_embed.add_field(embed_title, content)
            embed = build_embed.build()
            await ctx.send(content=amount_update.message, embed=embed)
            return

        await ctx.send(amount_update.message)
        
    @bot.command(name="cur-token")
    async def currency_update_token(ctx, *, args:str):
        try:
            token, reason = parse_csv_args(args, 2)            
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.cur-token* `New Amount`, `Reason`", 
                delete_after=20)
            return
        
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        token_update = service.currency_service.update_currency_token(game_id, token, reason)
        if not token_update.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(token_update.message), 
                delete_after=20)

        await ctx.send(token_update.message)

    # logs on every action like spending or pulling. figure it out how or where to put this logging <- figured it out, logs on service.
    @bot.command(name="cur-logs")
    async def currency_update_amount(ctx):
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        currency_logs = service.currency_service.get_game_currency_action_logs(game_id)
        if not currency_logs.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(currency_logs.message), 
                delete_after=20)

        # Create Table of Currency Logs
        view = PaginatedTable(
            setting_service=service.settings_service,
            items=currency_logs.data,
            title="Currency Logs",
            timeout=60
        )

        message = await ctx.send(
            embed=view.build_embed(),
            view=view
        )

        view.message = message