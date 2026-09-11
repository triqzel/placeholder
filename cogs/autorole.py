import discord
from discord.ext import commands
from database import set_autorole, get_autorole
import config


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_authorized(self, ctx):
        if ctx.author.id == config.OWNER_ID:
            return True
        return ctx.author.guild_permissions.administrator

    @commands.command(name="autorole")
    @commands.guild_only()
    async def set_autorole_cmd(self, ctx, role: discord.Role):
        if not self.is_admin_or_authorized(ctx):
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        await set_autorole(ctx.guild.id, role.id)
        await ctx.send(f"✅ Auto-role set to {role.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role_id = await get_autorole(member.guild.id)
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                except Exception as e:
                    print(f"Failed to add auto-role: {e}")


async def setup(bot):
    await bot.add_cog(AutoRole(bot))
