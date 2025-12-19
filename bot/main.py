import discord,os,json,logging,asyncio
from discord.ext import commands,tasks
from aiohttp import web
from pathlib import Path
logging.basicConfig(level=logging.INFO)
log=logging.getLogger()
intents=discord.Intents.all()
bot=commands.Bot(command_prefix='!',intents=intents)
cfg_path=Path('./config/cfg.json')
state_path=Path('./config/state.json')
wh_path=Path('./config/webhooks.json')
msgs_path=Path('./config/messages.json')
async def load_cfg():
 if cfg_path.exists():
  with open(cfg_path)as f:return json.load(f)
 return{"api":{"url":"","token":""},"roles":{},"chans":{},"perms":{}}
async def save_cfg(c):
 cfg_path.parent.mkdir(parents=True,exist_ok=True)
 with open(cfg_path,'w')as f:json.dump(c,f,indent=2)
async def load_wh():
 if wh_path.exists():
  with open(wh_path)as f:return json.load(f)
 return{"webhooks":[]}
async def save_wh(w):
 with open(wh_path,'w')as f:json.dump(w,f,indent=2)
async def load_st():
 if state_path.exists():
  with open(state_path)as f:return json.load(f)
 return{"last_sync":None,"teams":[],"challs":[],"solves":[]}
async def load_msgs():
 if msgs_path.exists():
  with open(msgs_path)as f:return json.load(f)
 return{"messages":{}}
async def save_st(s):
 with open(state_path,'w')as f:json.dump(s,f,indent=2)
cfg={}
wh={}
st={}
class API:
 def __init__(self,url,token):self.url=url;self.token=token
 async def get(self,ep):
  try:
   import aiohttp
   async with aiohttp.ClientSession()as s:
    async with s.get(f"{self.url}{ep}",headers={"Authorization":f"Bearer {self.token}"})as r:
     return await r.json()if r.status==200 else None
  except:return None
 async def teams(self):return await self.get("/teams")
 async def challs(self):return await self.get("/challenges")
 async def score(self):return await self.get("/scoreboard")
 async def solves(self):return await self.get("/solves")
class Prov:
 def __init__(self,b,c):self.bot=b;self.cfg=c
 async def build(self,g):
  try:
   log.info(f"Building {g.name}...")
   await self._mk_roles(g)
   await self._mk_cats(g)
   await self._set_perms(g)
   await self._post_msgs(g)
   log.info("Build complete")
   return True
  except Exception as e:log.error(f"Build err: {e}");return False
 async def _post_msgs(self,g):
  m=await load_msgs()
  msgs_default={"announcements":"📢 **ANNOUNCEMENTS**\nOfficial project updates and news posted here. Check pinned messages for important information.","welcome":"👋 **Welcome to Discord Server Builder Community!**\nWe're building the next-gen CTF platform. Read #rules and #faq before diving in!","rules":"📋 **Server Rules**\n1. Be respectful\n2. No spam/self-promotion without permission\n3. Keep discussions on-topic\n4. Report issues to moderators\n5. Have fun!","general-chat":"💬 **General Discussion**\nAny non-project chat here. Get to know the community!","introductions":"🎯 **Introduce Yourself**\nTell us who you are, what you do, and why you're interested in Discord Server Builder!","troubleshooting":"🔧 **Troubleshooting**\nHaving issues? Post your problem and the community will help. Include error messages & steps to reproduce.","bug-reports":"🐛 **Bug Reports**\nFound a bug? Report it here with:\n1. Description\n2. Steps to reproduce\n3. Expected vs actual behavior\n4. Screenshots if possible","feature-requests":"💡 **Feature Requests**\nHave an idea? Suggest it here! React with ⬆️ to upvote ideas you like.","faq":"❓ **Frequently Asked Questions**\n**Q: How do I install Discord Server Builder?**\nA: Check #setup-guide\n\n**Q: How do I report a bug?**\nA: Use #bug-reports\n\n**Q: Can I contribute?**\nA: Yes! Check #github-updates for how to get started","github-updates":"🔗 **GitHub Updates**\nAutomatic commits, PRs, and releases posted here.","pull-requests":"📝 **Pull Requests**\nDiscuss and review pull requests. Link to PRs and discuss changes.","code-review":"👀 **Code Review**\nPeer code review discussions. Keep feedback constructive and helpful.","architecture":"🏗️ **Architecture Discussions**\nDesign decisions, system architecture, and technical discussions.","docs":"📚 **Documentation**\nDocs, guides, and tutorials for users and developers.","tutorials":"🎓 **Tutorials**\nStep-by-step guides on using Discord Server Builder. Share your own!","setup-guide":"🚀 **Setup Guide**\nComplete installation and setup instructions. Start here!","api-reference":"📖 **API Reference**\nAPI documentation and endpoint descriptions.","mod-actions":"⚖️ **Moderator Actions**\n🔒 MODS ONLY - Moderation decisions logged here.","mod-reports":"📢 **Mod Reports**\n🔒 MODS ONLY - User reports and cases discussed here.","warnings-log":"⚠️ **Warnings Log**\n🔒 MODS ONLY - Record of user warnings and actions.","internal-notes":"📝 **Internal Notes**\n🔒 MODS ONLY - Private notes for moderation team.","bot-logs":"🤖 **Bot Logs**\n🔐 ADMIN ONLY - Bot activity and system logs.","admin-commands":"⚙️ **Admin Commands**\n🔐 ADMIN ONLY - Test bot commands here.","audit-log":"📋 **Audit Log**\n🔐 ADMIN ONLY - All admin actions logged.","security":"🔐 **Security**\n🔐 ADMIN ONLY - Security alerts and incidents."}
  for c,d in msgs_default.items():
   try:
    ch=discord.utils.get(g.channels,name=c)
    if ch:
     async for msg in ch.history(limit=1):
      if msg.author==self.bot.user:return
     txt=m.get("messages",{}).get(c,d)
     msg=await ch.send(txt)
     await msg.pin(reason="Setup")
     log.info(f"✓ {c}")
   except:pass
 async def _mk_roles(self,g):
  for r,c in self.cfg["roles"].items():
   try:
    if not discord.utils.get(g.roles,name=r):
     await g.create_role(name=r,color=discord.Color.from_str(c),reason="Auto-build")
     log.info(f"✓ Role: {r}")
   except:pass
 async def _mk_cats(self,g):
  for cat,chans in self.cfg["chans"].items():
   try:
    ec=discord.utils.get(g.categories,name=cat)
    if not ec:ec=await g.create_category(name=cat,reason="Auto-build")
    for c in chans:
     if not discord.utils.get(g.channels,name=c):
      await g.create_text_channel(name=c,category=ec,reason="Auto-build")
      log.info(f"✓ Channel: {c}")
   except:pass
 async def _set_perms(self,g):
  for cat,perms in self.cfg["perms"].items():
   try:
    ec=discord.utils.get(g.categories,name=cat)
    if ec:
     for c in ec.channels:
      for r,p in perms.items():
       role=discord.utils.get(g.roles,name=r)
       if role:
        await c.set_permissions(role,view_channel=p.get("view",True),send_messages=p.get("send",False))
   except:pass
prov=None
@bot.event
async def on_ready():
 global cfg,wh,st,prov
 cfg=await load_cfg()
 wh=await load_wh()
 st=await load_st()
 if not prov:prov=Prov(bot,cfg)
 log.info(f"{bot.user} online")
 await load_cogs()
 try:
  s=await bot.tree.sync()
  log.info(f"Synced {len(s)} commands")
 except Exception as e:log.error(f"Tree sync err: {e}")
 await create_web()
async def load_cogs():
 cog_dir=Path("./cogs")
 if cog_dir.exists():
  for f in cog_dir.glob("*.py"):
   if not f.name.startswith("_"):
    try:
     await bot.load_extension(f"cogs.{f.stem}")
     log.info(f"✓ Cog: {f.stem}")
    except Exception as e:log.error(f"Cog err {f.stem}: {e}")
@bot.tree.command(name="setup",description="Build server")
async def setup(ctx):
 if not any(r.name in["Organizer","Bot Admin"]for r in ctx.author.roles):
  await ctx.response.send_message("No perms",ephemeral=True)
  return
 await ctx.response.defer()
 ok=await prov.build(ctx.guild)
 await ctx.followup.send("✓ Server built"if ok else"✗ Build failed")
@bot.tree.command(name="sync",description="Sync from API")
async def sync(ctx):
 if not any(r.name in["Organizer"]for r in ctx.author.roles):
  await ctx.response.send_message("No perms",ephemeral=True)
  return
 await ctx.response.defer()
 if not cfg.get("api",{}).get("url"):
  await ctx.followup.send("API not cfg'd")
  return
 api=API(cfg["api"]["url"],cfg["api"]["token"])
 t=await api.teams()
 c=await api.challs()
 s=await api.score()
 st["last_sync"]=str(asyncio.get_event_loop().time())
 st["teams"]=t or[]
 st["challs"]=c or[]
 await save_st(st)
 await ctx.followup.send(f"✓ Synced: {len(t or[])} teams, {len(c or[])} challs")
@bot.tree.command(name="rebuild",description="Rebuild server")
async def rebuild(ctx):
 if not any(r.name in["Organizer"]for r in ctx.author.roles):
  await ctx.response.send_message("No perms",ephemeral=True)
  return
 await ctx.response.defer()
 ok=await prov.build(ctx.guild)
 await ctx.followup.send("✓ Rebuilt"if ok else"✗ Failed")
@bot.tree.command(name="wh_add",description="Add webhook")
async def wh_add(ctx,trig:str,url:str):
 if not any(r.name in["Organizer"]for r in ctx.author.roles):
  await ctx.response.send_message("No perms",ephemeral=True)
  return
 wh["webhooks"].append({"id":len(wh["webhooks"]),"trigger":trig,"url":url,"active":True})
 await save_wh(wh)
 await ctx.response.send_message(f"✓ Webhook added: {trig}")
@bot.tree.command(name="wh_list",description="List webhooks")
async def wh_list(ctx):
 if not any(r.name in["Organizer"]for r in ctx.author.roles):
  await ctx.response.send_message("No perms",ephemeral=True)
  return
 if not wh["webhooks"]:
  await ctx.response.send_message("No webhooks")
  return
 msg="\n".join([f"{w['id']}: {w['trigger']} → {w['url']}"for w in wh["webhooks"]])
 await ctx.response.send_message(f"```{msg}```")
@bot.tree.command(name="wh_del",description="Del webhook")
async def wh_del(ctx,id:int):
 if not any(r.name in["Organizer"]for r in ctx.author.roles):
  await ctx.response.send_message("No perms",ephemeral=True)
  return
 wh["webhooks"]=[w for w in wh["webhooks"]if w["id"]!=id]
 await save_wh(wh)
 await ctx.response.send_message(f"✓ Webhook {id} removed")
async def f_wh(evt,dat):
 for w in wh["webhooks"]:
  if w["trigger"]==evt and w.get("active"):
   try:
    import aiohttp
    async with aiohttp.ClientSession()as s:
     async with s.post(w["url"],json=dat,timeout=5)as r:
      log.info(f"Webhook fired: {evt}")
   except Exception as e:log.error(f"Webhook err: {e}")
async def h_chk(r):return web.json_response({"status":"ok","bot":"online"if bot.is_ready()else"offline"})
async def h_cfg(r):return web.json_response(cfg)
async def create_web():
 app=web.Application()
 app.router.add_get("/health",h_chk)
 app.router.add_get("/cfg",h_cfg)
 runner=web.AppRunner(app)
 await runner.setup()
 site=web.TCPSite(runner,"0.0.0.0",3030)
 await site.start()
 log.info("Web srv on 3030")
if __name__=="__main__":
 token=os.getenv("DISCORD_BOT_TOKEN")
 if token:
  bot.run(token)
 else:
  log.warning("DISCORD_BOT_TOKEN not set - bot will not connect to Discord")
  log.info("Set it in .env then restart")
  asyncio.run(create_web())
  import time
  try:
   while True:time.sleep(1)
  except KeyboardInterrupt:pass
