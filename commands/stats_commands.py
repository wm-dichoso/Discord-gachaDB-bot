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

def setup_stats_commands(bot, service: ServicesProtocol):
    @bot.command(name="stats")
    async def get_overview(ctx):
        game = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(game.message), 
                delete_after=20)        
        game_id = game.data['Game_ID']
        game_name = game.data['Game_Name']

        overview = service.stats_service.get_game_pull_overview(game_id)
        if not overview.success:
            return await ctx.send(
                "⚠ SERVICE ERROR:"+ str(overview.message), 
                delete_after=20)
        embed_title = str(game_name) + " Pulls Overview"
        build_embed = (
            SimpleEmbed(
                title = embed_title,
                color = 0x00AE86
            )
        )
        build_embed.add_field(name="Total SSRs: ", value=overview.data["Total_SSR"])
        build_embed.add_field(name="Total Pulls: ", value=overview.data["Total_Pulls"])
        build_embed.add_field(name="SSRs Rate: ", value=overview.data["SSR_Rate"])
        build_embed.add_field(name="Averge Pull per SSR: ", value=overview.data["Average_Pull"])
            
        embed = build_embed.build()
        await ctx.send(embed=embed)