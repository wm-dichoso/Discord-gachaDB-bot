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

def setup_banner_commands(bot, service: ServicesProtocol):
    @bot.command(name="addbanner")
    async def create_banner(ctx, *, args: str):
        try:
            banner_name, pity, max_pity = parse_csv_args(args, 3)            
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.create_banner `Banner Name`, `pity`, `max pity`*", 
                delete_after=5)
            return

        # get game id for the channel !!!
        get_game_id = service.game_service.get_game_for_channel(ctx.channel.id)
        
        if not get_game_id.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(get_game_id.message), delete_after=5)
            return
        
        game_id = get_game_id.data['Game_ID']

        banner = service.banner_service.create_banner(game_id, banner_name, pity, max_pity)

        if not banner.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(banner.message))
            return
        
        await ctx.send(banner.message)

    @bot.command(name="banners")
    async def list_game_banners(ctx):
        # get game id for the channel !!!
        get_game_id = service.game_service.get_game_for_channel(ctx.channel.id)
        if not get_game_id.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(get_game_id.message), delete_after=5)
            return
        
        game_id = get_game_id.data['Game_ID']
        game_name = get_game_id.data['Game_Name']

        banners = service.banner_service.get_banners(game_id)
        if not banners.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(banners.message), delete_after=5)
            return
        
        banner_list = [
            {
                "name": f'ID: {b['Banner_ID']} | {b["Banner_Name"]} | At *{b["Current_Pity"]} pity*. | '
                        f'Last accessed: {b["Last_Updated"]}',
                "id": b["Banner_ID"]
            }
            for b in banners.data
        ]

        banner_menu = SelectionMenu(bot, items=banner_list, title=f"🎴 Select a Banner for {game_name}")

        async def on_banner_select(interaction: discord.Interaction, selected_banner, index):
            await interaction.response.edit_message(embed=banner_menu.build_embed(), view=None)
            
            banner_id = selected_banner["id"]

            # GET PULL HISTORY
            history = service.pull_service.get_banner_pulls(banner_id)
            
            # DO VALIDATION HERE: CHECK IF THE GAME HAS BANNER LIST
            if not history.success:
                await ctx.send("⚠ SERVICE ERROR: " + str(history.message))
                return

            # Create Table of Pull history
            view = PaginatedTable(
                items=history.data,
                title="History"
            )

            await interaction.followup.send(
                embed=view.build_embed(),
                view=view
            )

        banner_menu.set_callback(on_banner_select)
        await banner_menu.send(ctx.channel)

    @bot.command(name="ubp")
    async def update_banner_pity(ctx, *, args: str):
        try:
            banner_id, pity, max_pity = parse_csv_args(args, 3)            
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.ubp `Banner ID`, `pity`, `max pity`*", 
                delete_after=5)
            return

        update = service.banner_service.update_pity_detail(banner_id, pity, max_pity)

        if not update.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(update.message))
                
        await ctx.send(update.message)

    @bot.command(name="ubn")
    async def update_banner_name(ctx, *, args: str):
        try:
            banner_id, name = parse_csv_args(args, 2)
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.ubn* `Banner ID`, `New Banner Name`", 
                delete_after=5)
            return

        update = service.banner_service.update_banner_name(banner_id, name)

        if not update.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(update.message))
                
        await ctx.send(update.message)

    @bot.command(name="pull")
    async def add_pull(ctx, *, args: str):
        get_game_id = service.game_service.get_game_for_channel(ctx.channel.id)
        if not get_game_id.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(get_game_id.message), delete_after=5)
            return
        
        game_id = get_game_id.data['Game_ID']
        game_name = get_game_id.data['Game_Name']

        banners = service.banner_service.get_banners(game_id)
        if not banners.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(banners.message), delete_after=5)
            return
        
        banner_list = [
            {
                "name": f'{b["Banner_Name"]} | At *{b["Current_Pity"]} pity*. |'
                        f'Last accessed: {b["Last_Updated"]}',
                "id": b["Banner_ID"]
            }
            for b in banners.data
        ]

        embed_builder = (
            SimpleEmbed(title="List of Banners")
            .set_footer(f"from the game: {game_name}")
        )

        for i, banner in enumerate(banner_list, start=1):
            embed_builder.add_field(
                name=f"{i}. {banner['name']}",
                value=f"ID: {banner['id']}",
                inline=False
            )

        embed = embed_builder.build()

        try:
            banner_id, entry, pity, notes = parse_csv_args(args, 4)
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.pull* `Entry Name`, `pity`, `Notes: Optional`", 
                embed=embed, delete_after=10)
            return
        
        add = service.pull_service.add_pull_to_banner(entry, banner_id, pity, notes)
        if not add.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(add.message))
            return
    
        await ctx.send(f"⚠ SERVICE MESSAGE: `{add.message}`", 
                delete_after=10)


    @bot.command(name="pity")
    async def show_pity(ctx, banner_id):
        if not banner_id:
            await ctx.send(
                "⚠ WARNING Command Format: *.pity* `Banner ID`", 
                delete_after=10)
            return
        
        # get game details then banner details

        game = service.game_service.get_game_for_channel(ctx.channel.id)
        if not game.success:
            return await ctx.send("⚠ SERVICE ERROR: " + str(game.message))        
        game_name = game.data["Game_Name"]
        
        banner = service.banner_service.get_banner(banner_id)
        if not banner.success:
            return await ctx.send("⚠ SERVICE ERROR: " + str(banner.message))        
        banner_id, game_id, banner_name, current_pity, max_pity, last_updated = banner.data.values()

        # embed for banner info
        embed_build = (
            SimpleEmbed(
                title=game_name,
                color=0x00AE86
            )
            .set_footer("Last Updated: " + str(last_updated))
        )
        table = f"Current Pity: {current_pity} / {max_pity}"
        embed_build.add_field(banner_name, f"```{table}```")
        embed = embed_build.build()

        await ctx.send(embed=embed)
            
        
    @bot.command(name="em")
    async def embed(ctx):
        embed = (
            SimpleEmbed(
                title="List of Banners",
                color=0x00AE86
            )
            .add_field("Weird", "The quick brown fox jumps over the lazy dog\nThe quick brown fox jumps over the lazy dog")
            .add_field("Title in here", "Whatever this is", inline=True)
            .set_footer("Powered by discord.py")
            .build()
        )
        await ctx.send(embed=embed)

    @bot.command(name="emb")
    async def embedder(ctx, *, args: str):
        try:
            title, content, footer = parse_csv_args(args, 3)
        except ValueError:
            await ctx.send(
                "⚠ WARNING Command Format: *.emb* `Title`, `content`, `footer: Optional`", 
                embed=embed, delete_after=10)
            return

        build_embed = (
            SimpleEmbed(
                title = title,
                color = 0x00AE86
            )
        )
        build_embed.add_field(content)
        embed = build_embed.build()
        await ctx.send(embed=embed)