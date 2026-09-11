import discord
from discord.ext import commands
from discord import ui
import os
from dotenv import load_dotenv
from datetime import timedelta
import aiosqlite

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
PREFIX = os.getenv("COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

DB_PATH = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                autorole_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS voice_channels (
                channel_id INTEGER PRIMARY KEY,
                owner_id INTEGER
            )
        """)
        await db.commit()

async def get_autorole(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT autorole_id FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def set_autorole(guild_id, role_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO guild_settings (guild_id, autorole_id) VALUES (?, ?)", (guild_id, role_id))
        await db.commit()

async def get_voice_owner(channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT owner_id FROM voice_channels WHERE channel_id = ?", (channel_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def add_voice_channel(channel_id, owner_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO voice_channels (channel_id, owner_id) VALUES (?, ?)", (channel_id, owner_id))
        await db.commit()

async def remove_voice_channel(channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM voice_channels WHERE channel_id = ?", (channel_id,))
        await db.commit()

def is_admin(ctx):
    return ctx.author.id == OWNER_ID or ctx.author.guild_permissions.administrator

@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    print(f"📊 Serving {len(bot.guilds)} guild(s)")

@bot.event
async def on_member_join(member):
    role_id = await get_autorole(member.guild.id)
    if role_id:
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role)
                print(f"✅ Added auto-role to {member}")
            except Exception as e:
                print(f"❌ Failed to add auto-role: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        if after.channel.name.lower() == "➕ create vc":
            try:
                category = after.channel.category
                vc_name = f"{member.name}'s VC"
                new_vc = await category.create_voice_channel(vc_name)
                await add_voice_channel(new_vc.id, member.id)
                await member.move_to(new_vc)
                print(f"✅ Created VC for {member}")
            except Exception as e:
                print(f"❌ Failed to create VC: {e}")

    if after.channel is None and before.channel is not None:
        owner = await get_voice_owner(before.channel.id)
        if owner and member.id == owner and len(before.channel.members) == 0:
            try:
                await remove_voice_channel(before.channel.id)
                await before.channel.delete()
                print(f"✅ Deleted empty voice channel")
            except Exception as e:
                print(f"❌ Failed to delete voice channel: {e}")

class VoiceControlView(ui.View):
    def __init__(self, channel, owner_id):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner_id = owner_id

    async def interaction_check(self, interaction):
        if interaction.user.id != self.owner_id and interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the owner can use these controls.", ephemeral=True)
            return False
        return True

    @ui.button(label="Rename", style=discord.ButtonStyle.blurple, emoji="✏️")
    async def rename(self, interaction, button):
        await interaction.response.send_modal(RenameModal(self.channel))

    @ui.button(label="Lock", style=discord.ButtonStyle.danger, emoji="🔒")
    async def lock(self, interaction, button):
        try:
            await self.channel.edit(user_limit=len(self.channel.members))
            await interaction.response.send_message(f"🔒 Locked!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @ui.button(label="Unlock", style=discord.ButtonStyle.success, emoji="🔓")
    async def unlock(self, interaction, button):
        try:
            await self.channel.edit(user_limit=0)
            await interaction.response.send_message(f"🔓 Unlocked!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete(self, interaction, button):
        try:
            await remove_voice_channel(self.channel.id)
            await self.channel.delete()
            await interaction.response.send_message(f"✅ Deleted!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class RenameModal(ui.Modal, title="Rename Channel"):
    name = ui.TextInput(label="New Name", max_length=100)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction):
        try:
            await self.channel.edit(name=self.name.value)
            await interaction.response.send_message(f"✅ Renamed to **{self.name.value}**", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.command(name="autorole")
@commands.guild_only()
async def autorole(ctx, role: discord.Role):
    if not is_admin(ctx):
        await ctx.send("❌ Admin only")
        return
    await set_autorole(ctx.guild.id, role.id)
    await ctx.send(f"✅ Auto-role set to {role.mention}")

@bot.command(name="ban")
@commands.guild_only()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not is_admin(ctx):
        await ctx.send("❌ Admin only")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member} banned. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name="kick")
@commands.guild_only()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not is_admin(ctx):
        await ctx.send("❌ Admin only")
        return
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member} kicked. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name="timeout")
@commands.guild_only()
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No reason"):
    if not is_admin(ctx):
        await ctx.send("❌ Admin only")
        return
    try:
        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)
        await ctx.send(f"✅ {member} timed out for {minutes}m. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name="purge")
@commands.guild_only()
async def purge(ctx, amount: int):
    if not is_admin(ctx):
        await ctx.send("❌ Admin only")
        return
    if amount > 100:
        await ctx.send("❌ Max 100 messages")
        return
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"✅ Deleted {len(deleted)-1} messages")
        await msg.delete(delay=3)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name="createvc")
@commands.guild_only()
async def createvc(ctx, *, name="New VC"):
    try:
        category = ctx.author.voice.channel.category if ctx.author.voice else None
        if not category:
            category = discord.utils.get(ctx.guild.categories, name="Voice")
        if not category:
            category = await ctx.guild.create_category("Voice")

        vc = await category.create_voice_channel(name)
        await add_voice_channel(vc.id, ctx.author.id)

        embed = discord.Embed(title="✅ Voice Channel Created", description=f"Channel: {vc.mention}", color=discord.Color.green())
        view = VoiceControlView(vc, ctx.author.id)
        await ctx.send(embed=embed, view=view)

        try:
            await ctx.author.move_to(vc)
        except:
            pass
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name="vcinfo")
@commands.guild_only()
async def vcinfo(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ You're not in a voice channel")
        return

    vc = ctx.author.voice.channel
    owner_id = await get_voice_owner(vc.id)

    embed = discord.Embed(title=vc.name, color=discord.Color.blue())
    embed.add_field(name="Members", value=len(vc.members))
    embed.add_field(name="Owner", value=f"<@{owner_id}>" if owner_id else "Unknown")
    embed.add_field(name="Bitrate", value=f"{vc.bitrate//1000}kbps")
    embed.add_field(name="Limit", value=vc.user_limit or "Unlimited")

    if owner_id == ctx.author.id or ctx.author.id == OWNER_ID:
        view = VoiceControlView(vc, owner_id)
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send(embed=embed)

async def main():
    await init_db()
    print("✅ Database initialized")
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
