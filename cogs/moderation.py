import discord
from discord.ext import commands
from datetime import timedelta
import config


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_authorized(self, ctx):
        if ctx.author.id == config.OWNER_ID:
            return True
        return ctx.author.guild_permissions.administrator

    @commands.command(name="kick")
    @commands.guild_only()
    async def kick_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if not self.is_admin_or_authorized(ctx):
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        if member.top_role >= ctx.author.top_role and ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ You cannot kick someone with a higher or equal role.")
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="User Kicked",
                description=f"{member.mention} has been kicked.",
                color=discord.Color.orange(),
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Kicked by", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to kick: {e}")

    @commands.command(name="ban")
    @commands.guild_only()
    async def ban_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if not self.is_admin_or_authorized(ctx):
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        if member.top_role >= ctx.author.top_role and ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ You cannot ban someone with a higher or equal role.")
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="User Banned",
                description=f"{member.mention} has been banned.",
                color=discord.Color.red(),
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Banned by", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to ban: {e}")

    @commands.command(name="timeout")
    @commands.guild_only()
    async def timeout_user(self, ctx, member: discord.Member, duration: int, *, reason="No reason provided"):
        """Timeout a user for duration (in minutes)"""
        if not self.is_admin_or_authorized(ctx):
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        if member.top_role >= ctx.author.top_role and ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ You cannot timeout someone with a higher or equal role.")
            return

        try:
            timeout_until = discord.utils.utcnow() + timedelta(minutes=duration)
            await member.timeout(timeout_until, reason=reason)
            embed = discord.Embed(
                title="User Timed Out",
                description=f"{member.mention} has been timed out.",
                color=discord.Color.yellow(),
            )
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Timed out by", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to timeout: {e}")

    @commands.command(name="purge")
    @commands.guild_only()
    async def purge_messages(self, ctx, amount: int):
        """Delete the last X messages (max 100)"""
        if not self.is_admin_or_authorized(ctx):
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        if amount > 100:
            await ctx.send("❌ Cannot purge more than 100 messages at once.")
            return

        if amount < 1:
            await ctx.send("❌ Amount must be at least 1.")
            return

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            embed = discord.Embed(
                title="Messages Purged",
                description=f"Deleted {len(deleted) - 1} messages from {ctx.channel.mention}",
                color=discord.Color.green(),
            )
            embed.add_field(name="Purged by", value=ctx.author.mention, inline=False)
            msg = await ctx.send(embed=embed)
            await msg.delete(delay=5)
        except Exception as e:
            await ctx.send(f"❌ Failed to purge: {e}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
