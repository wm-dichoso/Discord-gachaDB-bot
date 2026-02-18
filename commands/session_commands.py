from discord.ext import commands
import discord
from services.interface import ServicesProtocol
from services import Services
from UI.SelectionMenu import SelectionMenu
from UI.TableView import PaginatedTable
from UI.SimpleEmbed import SimpleEmbed

# save session data here?
session_id = 0
session_name = ""
session_break_id = 0

def setup_session_commands(bot, service: ServicesProtocol):
    @bot.command(name="sesh")
    async def start_session(ctx, *, name: str):
        global session_id, session_name
        if not session_id == 0:
            await ctx.send("⚠ SERVICE ERROR: " + "Session already started. Cannot start another session.", delete_after=5)
            return
        
        start = service.session_service.start_session(name)
        
        if not start.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(start.message), delete_after=5)
            return
        
        session_id = start.data
        session_name = name

        await ctx.send(start.message + " *" + name +"* On session id: "+ str(start.data))

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

    @bot.command(name="brk")
    async def add_break(ctx):
        global session_id, session_name, session_break_id
        if session_id == 0:
            await ctx.send("⚠ SERVICE ERROR: " + "No active session to add break to.", delete_after=5)
            return
        
        if not session_break_id == 0:
            await ctx.send("⚠ SERVICE ERROR: " + "Break session already active.", delete_after=5)
            return
        
        break_start = service.session_service.add_session_break(session_id)

        if not break_start.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(break_start.message), delete_after=5)
            return
        
        session_break_id = break_start.data
        
        await ctx.send(str(break_start.message) + " For the Session name: *" + session_name+ "*")

    @bot.command(name="end_brk")
    async def end_break(ctx):
        global session_id, session_name, session_break_id
        if session_id == 0:
            await ctx.send("⚠ SERVICE ERROR: " + "No active session to end break for.", delete_after=5)
            return
        
        if session_break_id == 0:
            await ctx.send("⚠ SERVICE ERROR: " + "No active break session to end.", delete_after=5)
            return
        
        break_end = service.session_service.end_break(session_break_id)

        if not break_end.success:
            await ctx.send("⚠ SERVICE ERROR: " + str(break_end.message), delete_after=5)
            return
        
        session_break_id = 0
        
        await ctx.send("Break Session for session: **"+ session_name + "** ended in **" + str(break_end.data) + "** duration.")
    # TODO: 
    # delete a session
    # delete break
    # STATUS, check if theres current session on mem, check if theres break going. send the name etc etc
    