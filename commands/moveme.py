import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings

class MovemeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="moveme", description="ينقلك إلى الروم الصوتي الذي تختاره")
    @app_commands.describe(to="اختر الروم الصوتي الذي تريد الانتقال إليه")
    async def moveme(self, interaction: discord.Interaction, to: discord.VoiceChannel):
        # 1. التحقق من لوحة التحكم
        settings = load_settings()
        if not settings.get("moveme", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً.", ephemeral=True)

        # 2. التحقق هل العضو في روم صوتي حالياً؟
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message("❌ يجب أن تكون في روم صوتي أولاً لكي أتمكن من نقلك!", ephemeral=True)

        # 3. التحقق من صلاحيات البوت في الروم الهدف
        if not to.permissions_for(interaction.guild.me).move_members:
            return await interaction.response.send_message(f"❌ ليس لدي صلاحية (نقل الأعضاء) لنقلك إلى {to.mention}.", ephemeral=True)

        try:
            # 4. عملية النقل
            await interaction.user.move_to(to)
            
            embed = discord.Embed(
                description=f"✅ تم نقلك بنجاح إلى: {to.mention}",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ فشلت عملية النقل: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MovemeCog(bot))
