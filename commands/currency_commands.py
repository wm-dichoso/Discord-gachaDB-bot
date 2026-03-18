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

def setup_currency_commands(bot, service: ServicesProtocol):
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
        build_embed.add_field(name="Total Available Pulls: ", value=currency.data["Pull_Count"])
        if currency.data["Goal"] != 0:            
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
    
    @bot.command(name="cur-pullval")
    async def currency_add_pull_val(ctx, pull_val):
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        pull_val = service.currency_service.set_game_pull_value(game_id, pull_val)
        if not pull_val.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(pull_val.message), 
                delete_after=20)

        await ctx.send(pull_val.message)
    

    # remaking currency goal now with type so we can set goal with token not just amount 
    @bot.command(name="goal")
    async def set_game_currency_goal(ctx, *, args:str):
        try:
            type, amount = parse_csv_args(args, 2)            
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.goal* `Currency Type **[token]** / **[cur]**`, `Amount`", 
                delete_after=20)
            return
        
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        currency_goal = service.currency_service.set_new_currency_goal(game_id, type, amount)
        if not currency_goal.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(currency_goal.message), 
                delete_after=20)

        # goal data to embed
        goal_value = currency_goal.data["Currency_Goal"]
        current_balance = currency_goal.data["Current_balance"]
        days_needed = currency_goal.data["Estimate_days_needed"]
        
        build_embed = (
            SimpleEmbed(
                title = "Currency Goal Established",
                color = 0x00AE86
            )
        )
        build_embed.add_field(name="Currency Goal: ", value=goal_value)
        build_embed.add_field(name="Current Balance: ", value=current_balance)
        build_embed.add_field(name="Estimate days needed to reach: ", value=days_needed)
        embed = build_embed.build()

        await ctx.send(embed=embed)

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
        
        cur_data = amount_update.data
        
        if "Goal" in cur_data:
            build_embed = (
                SimpleEmbed(
                    title = "Goal Reached",
                    color = 0x00AE86
                )
            )

            currency_goal = str(cur_data['Goal'])
            pull_tokens = str(cur_data['Pull_tokens'])

            goal_title = "Currency Goal of "+ currency_goal
            goal_content = "is now Reached"
            build_embed.add_field(goal_title, goal_content)

            pull_avail_title = "You now have " + pull_tokens + " tokens"
            pull_content = "Available for pulling"
            build_embed.add_field(pull_avail_title, pull_content)

            embed = build_embed.build()
            await ctx.send(content=amount_update.message, embed=embed)
            return

        build_embed = (
            SimpleEmbed(
                title = "Currency Updated!",
                color = 0x00AE86
            )
        )

        tokens = str(cur_data)
        title = "You now have " + tokens + " tokens"
        content = "Available for pulling"
        build_embed.add_field(title, content)
        embed = build_embed.build()
        await ctx.send(content=amount_update.message, embed=embed)
        
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

    @bot.command(name="cur-logs")
    async def currency_history(ctx):
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

    # statistics
    @bot.command(name="cur-income")
    async def currency_income(ctx):
        game_info = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game_info.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game_info.message), 
                delete_after=20)        
        game_id = game_info.data['Game_ID']
        
        currency_income = service.currency_service.get_currency_income(game_id)
        if not currency_income.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(currency_income.message), 
                delete_after=20)
        
        # weekly, monthly stats, and monthly projection
        weekly = currency_income.data["Weekly_Income"]
        monthly = currency_income.data["Monthly_Income"]
        projected = currency_income.data["Projected_Income"]        
        projected_pulls = currency_income.data["Projected_Pulls"]
        
        # Embed for stats
        build_embed = (
            SimpleEmbed(
                title = "Currency Stats",
                color = 0x00AE86
            )
        )
        build_embed.add_field(name="Weekly Income: ", value=weekly)
        build_embed.add_field(name="Monthly Income: ", value=monthly)
        build_embed.add_field(name="This Month Projected Income: ", value=projected)
        build_embed.add_field(name="Projected Pulls for the month: ", value=projected_pulls)
        embed = build_embed.build()

        await ctx.send(embed=embed)
