from discord.ext import commands
import discord
from services.interface import ServicesProtocol
from services import Services
from UI.SelectionMenu import SelectionMenu
from UI.TableView import PaginatedTable
from UI.SimpleEmbed import SimpleEmbed

# save session data here?
session_id = 0

def setup_session_commands(bot, service: ServicesProtocol):
    @bot.command(name="sesh")
    async def start_session(ctx, *, name: str):
        global session_id
        if not session_id == 0:
            await ctx.send("⚠ SERVICE ERROR: " + "Session already started. Cannot start another session.", delete_after=5)
            return
        
        start = service.session_service.start_session(name)
        
        if not start.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(start.message), delete_after=5)
            return
        
        session_id = start.data

        await ctx.send(start.message + "*" + name +"* On session id: "+ str(start.data))

    @bot.command(name="end")
    async def end_sesh(ctx):
        global session_id
        if session_id == 0:
            await ctx.send("⚠ SERVICE ERROR: " + "No active session to end.", delete_after=5)
            return
        
        end = service.session_service.end_session(session_id)

        if not end.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(end.message), delete_after=5)
            return
        
        session_id = 0
        
        await ctx.send("Session **"+end.data["session_name"] + "** ended in **" + end.data["duration"] + "** duration.")
            
    @bot.command(name="sessions")
    async def list_sessions(ctx):
        result = service.session_service.browse_sessions()

        if not result.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(result.message), delete_after=5)
            return

        view = PaginatedTable(
            items=result.data,
            title="Session Lists"
        )

        await ctx.send(embed=view.build_embed(), view=view)

    # TODO: add session's break time
    # end the break
    # delete a session
    # delete break