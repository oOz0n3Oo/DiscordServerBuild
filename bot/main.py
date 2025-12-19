import discord
from discord.ext import commands
import os
import json
from pathlib import Path
import asyncio

CONFIG_DIR = Path('/app/config') if Path('/app/config').exists() else Path(__file__).parent / 'config'
cfg_path = CONFIG_DIR / 'cfg.json'
msgs_path = CONFIG_DIR / 'messages.json'

def load_cfg():
    if cfg_path.exists():
        with open(cfg_path) as f:
            return json.load(f)
    return {"roles": {}, "chans": {}, "perms": {}}

def load_msgs():
    if msgs_path.exists():
        with open(msgs_path) as f:
            return json.load(f)
    return {"messages": {}}

cfg = load_cfg()
msgs = load_msgs()

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


class Builder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="setup", description="Build server structure", guild_only=True)
    async def setup(self, ctx: discord.ApplicationContext):
        guild = ctx.guild or (ctx.interaction.guild if ctx.interaction else None)
        if not guild and ctx.guild_id:
            guild = self.bot.get_guild(ctx.guild_id)

        if not guild:
            await ctx.respond("❌ Could not get server info.", ephemeral=True)
            return

        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("❌ Admin only.", ephemeral=True)
            return

        await ctx.defer()

        global cfg, msgs
        cfg = load_cfg()
        msgs = load_msgs()

        if not cfg.get('roles') and not cfg.get('chans'):
            await ctx.followup.send("❌ Config empty!")
            return

        ok = await self.build_server(guild)
        await ctx.followup.send("✅ Done!" if ok else "❌ Failed")

    @discord.slash_command(name="nuke", description="Delete ALL non-default channels and roles", guild_only=True)
    async def nuke(self, ctx: discord.ApplicationContext):
        guild = ctx.guild or (ctx.interaction.guild if ctx.interaction else None)
        if not guild and ctx.guild_id:
            guild = self.bot.get_guild(ctx.guild_id)

        if not guild:
            await ctx.respond("❌ Could not get server info.", ephemeral=True)
            return

        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("❌ Admin only.", ephemeral=True)
            return

        await ctx.defer()

        deleted_roles = 0
        deleted_cats = 0
        deleted_chans = 0

        # Delete ALL categories and their channels
        for cat in list(guild.categories):
            try:
                # Delete all channels in category first
                for ch in list(cat.channels):
                    try:
                        await ch.delete(reason="Nuke command")
                        deleted_chans += 1
                        await asyncio.sleep(0.3)
                    except:
                        pass
                # Then delete the category
                await cat.delete(reason="Nuke command")
                deleted_cats += 1
                await asyncio.sleep(0.3)
            except:
                pass

        # Delete any remaining channels not in categories (except default ones Discord won't let you delete)
        for ch in list(guild.channels):
            if not isinstance(ch, discord.CategoryChannel):
                try:
                    await ch.delete(reason="Nuke command")
                    deleted_chans += 1
                    await asyncio.sleep(0.3)
                except:
                    pass

        # Delete ALL non-default roles (bot can't delete @everyone, managed roles, or roles above its own)
        for role in list(guild.roles):
            if role.is_default() or role.managed or role >= guild.me.top_role:
                continue
            try:
                await role.delete(reason="Nuke command")
                deleted_roles += 1
                await asyncio.sleep(0.3)
            except:
                pass

        await ctx.followup.send(f"💥 Nuked: {deleted_roles} roles, {deleted_cats} categories, {deleted_chans} channels")

    async def build_server(self, guild):
        created_roles = {}

        try:
            # ROLES
            for rname, rcolor in cfg.get('roles', {}).items():
                try:
                    existing = discord.utils.get(guild.roles, name=rname)
                    if existing:
                        created_roles[rname] = existing
                        continue
                    role = await guild.create_role(
                        name=rname,
                        color=discord.Color.from_str(rcolor),
                        mentionable=True
                    )
                    created_roles[rname] = role
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"Role error {rname}: {e}")

            # CATEGORIES AND CHANNELS
            for catname, ch_list in cfg.get('chans', {}).items():
                try:
                    cat = discord.utils.get(guild.categories, name=catname)
                    if not cat:
                        cat = await guild.create_category(name=catname)
                    await asyncio.sleep(0.2)

                    for chname in ch_list:
                        existing_ch = discord.utils.get(guild.channels, name=chname)
                        if not existing_ch:
                            if catname == "VOICE":
                                await guild.create_voice_channel(name=chname, category=cat)
                            else:
                                await guild.create_text_channel(name=chname, category=cat)
                            await asyncio.sleep(0.2)
                except Exception as e:
                    print(f"Channel error {catname}: {e}")

            # PERMISSIONS
            for catname, perm_dict in cfg.get('perms', {}).items():
                try:
                    cat = discord.utils.get(guild.categories, name=catname)
                    if not cat:
                        continue
                    for ch in cat.channels:
                        for rname, pdata in perm_dict.items():
                            role = discord.utils.get(guild.roles, name=rname)
                            if role:
                                overwrite = discord.PermissionOverwrite(
                                    view_channel=pdata.get("view", True),
                                    send_messages=pdata.get("send", False),
                                    connect=pdata.get("view", True) if isinstance(ch, discord.VoiceChannel) else None,
                                    speak=pdata.get("send", False) if isinstance(ch, discord.VoiceChannel) else None
                                )
                                await ch.set_permissions(role, overwrite=overwrite)
                        await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Perm error {catname}: {e}")

            # MESSAGES - Post, Pin, Delete pin notification
            messages_config = msgs.get("messages", {})
            for cat in guild.categories:
                for ch in cat.channels:
                    if not isinstance(ch, discord.TextChannel):
                        continue
                    try:
                        has_bot_msg = False
                        async for msg in ch.history(limit=10):
                            if msg.author == self.bot.user and msg.pinned:
                                has_bot_msg = True
                                break

                        if has_bot_msg:
                            continue

                        txt = messages_config.get(ch.name)
                        if not txt:
                            continue

                        sent_msg = await ch.send(txt)
                        await sent_msg.pin()
                        await asyncio.sleep(0.5)

                        # Delete "pinned a message" notification
                        async for sys_msg in ch.history(limit=5):
                            if sys_msg.type == discord.MessageType.pins_add:
                                await sys_msg.delete()
                                break

                        await asyncio.sleep(0.3)
                    except Exception as e:
                        print(f"Msg error {ch.name}: {e}")

            return True
        except Exception as e:
            print(f"Build error: {e}")
            return False


@bot.event
async def on_ready():
    print(f"Ready: {bot.user}")

bot.add_cog(Builder(bot))

token = os.getenv("DISCORD_BOT_TOKEN")
if token:
    bot.run(token)
else:
    print("No DISCORD_BOT_TOKEN")
