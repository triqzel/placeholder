import discord
from discord.ext import commands
from discord import ui
from database import add_voice_channel, remove_voice_channel, get_voice_channel_owner
import config


class VoiceControlView(ui.View):
    def __init__(self, channel: discord.VoiceChannel, owner_id: int):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner_id = owner_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id and interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message("❌ Only the voice channel owner can use these controls.", ephemeral=True)
            return False
        return True

    @ui.button(label="Rename", style=discord.ButtonStyle.blurple, emoji="✏️")
    async def rename_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RenameModal(self.channel))

    @ui.button(label="Lock", style=discord.ButtonStyle.danger, emoji="🔒")
    async def lock_button(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await self.channel.edit(user_limit=len(self.channel.members))
            await interaction.response.send_message(f"🔒 {self.channel.mention} is now locked.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to lock: {e}", ephemeral=True)

    @ui.button(label="Unlock", style=discord.ButtonStyle.success, emoji="🔓")
    async def unlock_button(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await self.channel.edit(user_limit=0)
            await interaction.response.send_message(f"🔓 {self.channel.mention} is now unlocked.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unlock: {e}", ephemeral=True)

    @ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await remove_voice_channel(self.channel.id)
            await self.channel.delete()
            await interaction.response.send_message(f"✅ Channel deleted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to delete: {e}", ephemeral=True)


class RenameModal(ui.Modal, title="Rename Voice Channel"):
    name_input = ui.TextInput(label="New Channel Name", placeholder="Enter new name", max_length=100)

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.channel.edit(name=self.name_input.value)
            await interaction.response.send_message(
                f"✅ Channel renamed to **{self.name_input.value}**", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to rename: {e}", ephemeral=True)


class VoiceMaster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is None and before.channel is not None:
            owner = await get_voice_channel_owner(before.channel.id)
            if owner and member.id == owner and len(before.channel.members) == 0:
                try:
                    await remove_voice_channel(before.channel.id)
                    await before.channel.delete()
                except Exception as e:
                    print(f"Failed to delete voice channel: {e}")

    @commands.command(name="createvc")
    @commands.guild_only()
    async def create_voice_channel(self, ctx, *, name="New Voice Channel"):
        """Create a custom voice channel"""
        try:
            category = ctx.author.voice.channel.category if ctx.author.voice else None
            if not category:
                category = discord.utils.get(ctx.guild.categories, name="Voice")
                if not category:
                    category = await ctx.guild.create_category("Voice")

            vc = await category.create_voice_channel(name)
            await add_voice_channel(vc.id, ctx.guild.id, ctx.author.id)

            embed = discord.Embed(
                title="Voice Channel Created",
                description=f"Your voice channel {vc.mention} has been created!",
                color=discord.Color.green(),
            )
            embed.add_field(name="Owner", value=ctx.author.mention, inline=False)
            embed.add_field(name="Channel", value=vc.mention, inline=False)

            view = VoiceControlView(vc, ctx.author.id)
            await ctx.send(embed=embed, view=view)

            try:
                await ctx.author.move_to(vc)
            except Exception:
                pass

        except Exception as e:
            await ctx.send(f"❌ Failed to create voice channel: {e}")

    @commands.command(name="vcinfo")
    @commands.guild_only()
    async def voice_channel_info(self, ctx):
        """Get info about your current voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You are not in a voice channel.")
            return

        vc = ctx.author.voice.channel
        owner_id = await get_voice_channel_owner(vc.id)

        embed = discord.Embed(
            title=vc.name,
            color=discord.Color.blue(),
        )
        embed.add_field(name="Channel ID", value=vc.id, inline=False)
        embed.add_field(name="Members", value=len(vc.members), inline=False)
        embed.add_field(name="Owner", value=f"<@{owner_id}>" if owner_id else "Unknown", inline=False)
        embed.add_field(name="Bitrate", value=f"{vc.bitrate // 1000}kbps", inline=False)
        embed.add_field(name="User Limit", value=vc.user_limit or "Unlimited", inline=False)

        if owner_id == ctx.author.id or ctx.author.id == config.OWNER_ID:
            view = VoiceControlView(vc, owner_id)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(VoiceMaster(bot))
